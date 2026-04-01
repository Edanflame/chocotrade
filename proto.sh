python -m grpc_tools.protoc \
  -I./protos \
  --python_out=./chocotrade/protos_generated \
  --grpc_python_out=./chocotrade/protos_generated \
  ./protos/service.proto

sed -i '' 's/import service_pb2/from . import service_pb2/g' chocotrade/protos_generated/service_pb2_grpc.py
