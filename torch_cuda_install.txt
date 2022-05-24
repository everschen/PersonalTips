怎么检查 torch 和 cuda版本是不是匹配

import torch 
print(torch.__version__)
print(torch.version.cuda) 
print(torch.cuda.is_available())


pip config set global.index-url  http://mirrors.aliyun.com/pypi/simple/


pip install torch==1.8.0+cu101 torchvision==0.9.0+cu101 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html


pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html



