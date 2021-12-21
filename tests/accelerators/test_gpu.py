# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unittest import mock

import torch

from pytorch_lightning import Trainer
from pytorch_lightning.accelerators import GPUAccelerator
from pytorch_lightning.plugins.precision.precision_plugin import PrecisionPlugin
from pytorch_lightning.plugins.training_type.dp import DataParallelPlugin
from tests.helpers import BoringModel
from tests.helpers.runif import RunIf


@RunIf(min_torch="1.8")
@RunIf(min_gpus=1)
def test_get_torch_gpu_stats(tmpdir):
    """Test GPU get_device_stats with Pytorch >= 1.8.0."""
    current_device = torch.device(f"cuda:{torch.cuda.current_device()}")
    GPUAccel = GPUAccelerator(
        training_type_plugin=DataParallelPlugin(parallel_devices=[current_device]), precision_plugin=PrecisionPlugin()
    )
    gpu_stats = GPUAccel.get_device_stats(current_device)
    fields = ["allocated_bytes.all.freed", "inactive_split.all.peak", "reserved_bytes.large_pool.peak"]

    for f in fields:
        assert any(f in h for h in gpu_stats.keys())


@RunIf(max_torch="1.7")
@RunIf(min_gpus=1)
def test_get_nvidia_gpu_stats(tmpdir):
    """Test GPU get_device_stats with Pytorch < 1.8.0."""
    current_device = torch.device(f"cuda:{torch.cuda.current_device()}")
    GPUAccel = GPUAccelerator(
        training_type_plugin=DataParallelPlugin(parallel_devices=[current_device]), precision_plugin=PrecisionPlugin()
    )
    gpu_stats = GPUAccel.get_device_stats(current_device)
    fields = ["utilization.gpu", "memory.used", "memory.free", "utilization.memory"]

    for f in fields:
        assert any(f in h for h in gpu_stats.keys())


@RunIf(min_gpus=1)
@mock.patch("torch.cuda.set_device")
def test_set_cuda_device(set_device_mock, tmpdir):
    model = BoringModel()
    trainer = Trainer(
        default_root_dir=tmpdir,
        fast_dev_run=True,
        accelerator="gpu",
        devices=1,
        enable_checkpointing=False,
        enable_model_summary=False,
        enable_progress_bar=False,
    )
    trainer.fit(model)
    set_device_mock.assert_called_once()
