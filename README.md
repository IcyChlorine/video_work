# video work

此repo中存放了我用manim制作的视频的（部分）代码。
This repository is for holding part of my video code.

由于我在视频制作中对manim进行了大量魔改，因此请不要对代码能直接跑起来这一件事抱有希望。这里的代码主要的用途是作为参考。
Do not expect the code here to be able to run on your machine, because I've done a lot of customization to manim lib.

如果确实想运行我的代码，请配合我个人主页中的manim和manimhub的对应分支运行。

> manimhub是我对manim进行魔改和定制化的大部分代码所在地。由于将代码直接写入manim主线并不是一件容易的事，因此我尽量将自定义功能通过继承的方式挪到manim主库外面，这样就可以在不改变manim主库的同时自定义manim的功能。

> 在我的manim(我主页中的fork，并非主库)和manimhub repo中，给每个视频都留了快照分支，用以保留视频渲染时的环境。

## Note

代码中的"precondition"和"postcondition"是Hoare Triple。我借鉴了这一方法以解决长Scene中前后逻辑交错混乱的问题。

配合vscode插件`Better Comments`食用更佳。