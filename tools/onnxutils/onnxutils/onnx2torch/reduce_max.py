import torch
from torch import nn


from onnxutils.common import OnnxModel, OnnxNode

from .registry import converter
from .utils import OnnxToTorchModule, OperationConverterResult, OnnxMapping


class TorchReduceMax(nn.Module, OnnxToTorchModule):
    def __init__(self, axis, keepdims):
        super().__init__()
        self.axis = axis
        self.keepdims = keepdims

    def forward(self, x):
        return torch.max(x, dim=self.axis, keepdim=self.keepdims)[0]


@converter(operation_type='ReduceMax', version=13)
def _(onnx_node: OnnxNode, onnx_model: OnnxModel) -> OperationConverterResult:
    axis = onnx_node.attributes().get('axes')
    keepdims = bool(onnx_node.attributes().get('keepdims', 1))

    assert len(axis) == 1, 'not implement'
    axis = axis[0]

    return OperationConverterResult(
        torch_module=TorchReduceMax(axis, keepdims),
        onnx_mapping=OnnxMapping(
            inputs=onnx_node.inputs(),
            outputs=onnx_node.outputs(),
        ),
    )