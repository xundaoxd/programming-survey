from onnx_model import OnnxModel
from registry import optimizer


@optimizer('eliminate-concat')
class EliminateConcat:
    @staticmethod
    def apply(onnx_model: OnnxModel) -> OnnxModel:
        input_name_map = {}
        nodes_to_remove = []
        for node in reversed(onnx_model.get_nodes_by_optype('Concat')):
            if len(node.input) == 1:
                input_name_map[node.output[0]] = node.input[0]
                nodes_to_remove.append(node)

        onnx_model.remap_input_names(input_name_map)
        onnx_model.remove_nodes(nodes_to_remove)
        return onnx_model