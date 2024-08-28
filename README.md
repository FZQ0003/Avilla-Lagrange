# avilla-lagrange

该项目仅作为可行性验证：利用[Avilla](https://github.com/GraiaProject/Avilla)的抽象能力，对接[另一个bot框架](https://github.com/LagrangeDev/lagrange-python)，使两个（或多个）框架集成于同一程序中。

如需应用于生产环境，请考虑使用[avilla-onebot-v11](https://github.com/GraiaProject/Avilla/tree/master/avilla/onebot/v11)和支持[Onebot-11标准](https://github.com/botuniverse/onebot-11)的平台。

该项目未经测试，含有大量bug和未实现功能，请慎重使用。

## 环境搭建

可以直接使用PDM等工具搭建，也可以参考[这个脚本](https://github.com/FZQ0003/Qi-Bot/blob/avilla/venv_script_avilla.sh)，搭建虚拟环境后把项目以软链接的形式丢进`site-packages`。
