import onnx
import torch
from torch import nn


from onnxutils.common import OnnxModel, OnnxNode

from .registry import converter
from .utils import OnnxToTorchModule, OperationConverterResult, onnx_mapping_from_node

func_mapping = {
    'Add': torch.add,
    'Sub': torch.sub,
    'Mul': torch.mul,
    'Div': torch.div,
    'Div_int': lambda a, b: torch.div(a, b, rounding_mode='trunc'),
    'Pow': torch.pow,
    'Equal': torch.equal,
    'Greater': torch.gt,
    'Less': torch.lt,
    'And': torch.logical_and,
    'LessOrEqual': torch.le,
}


class TorchBinaryOp(nn.Module, OnnxToTorchModule):
    def __init__(self, f):
        super().__init__()
        self.f = f

    def forward(self, x0, x1):
        return self.f(x0, x1)


@converter(operation_type='Equal', version=13)
@converter(operation_type='Greater', version=13)
@converter(operation_type='Less', version=13)
@converter(operation_type='LessOrEqual', version=16)
@converter(operation_type='And', version=7)
@converter(operation_type='Add', version=14)
@converter(operation_type='Sub', version=14)
@converter(operation_type='Mul', version=14)
@converter(operation_type='Div', version=14)
@converter(operation_type='Pow', version=15)
def _(onnx_node: OnnxNode, onnx_model: OnnxModel) -> OperationConverterResult:
    op_type = onnx_node.op_type()
    if op_type == 'Div':
        inputs = [
            onnx_model.get_vinfo_by_name(x)
            for x in onnx_node.inputs()
        ]
        for idx, input_name in enumerate(onnx_node.inputs()):
            if inputs[idx] is None:
                tensor = onnx_model.get_initializer_by_name(input_name)
                if tensor is not None:
                    inputs[idx] = tensor.proto().data_type
            else:
                inputs[idx] = inputs[idx].type.tensor_type.elem_type

        integer_types = (
            onnx.TensorProto.DataType.UINT8,
            onnx.TensorProto.DataType.INT8,
            onnx.TensorProto.DataType.UINT16,
            onnx.TensorProto.DataType.INT16,
            onnx.TensorProto.DataType.UINT32,
            onnx.TensorProto.DataType.INT32,
            onnx.TensorProto.DataType.UINT64,
            onnx.TensorProto.DataType.INT64,
            onnx.TensorProto.DataType.UINT4,
            onnx.TensorProto.DataType.INT4,
        )
        if all(x in integer_types for x in inputs):
            op_type = 'Div_int'

    return OperationConverterResult(
        torch_module=TorchBinaryOp(func_mapping[op_type]),
        onnx_mapping=onnx_mapping_from_node(onnx_node),
    )
