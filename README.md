# video work

此repo中存放了我用`manim`制作的视频的（部分）代码。

This repository is for holding part of my video code.

由于我在视频制作中对`manim`进行了大量魔改，因此请不要对代码能直接跑起来这一件事抱有希望。这里的代码主要的用途是作为参考。

Do not expect the code here to be able to run on your machine, because I've done a lot of customization to manim lib.

如果确实想运行我的代码，请配合我个人主页中的`manim`和`manimhub`的对应分支运行。

> `manimhub`是我对`manim`进行魔改和定制化的大部分代码所在地。由于将代码直接写入`manim`主线并不是一件容易的事，因此我尽量将自定义功能通过继承的方式挪到`manim`主库外面，这样就可以在不改变`manim`主库的同时自定义`manim`的功能。

> 在我的`manim`(我主页中的fork，不是主库)和`manimhub` repo中，给每个视频都留了快照分支，用以保留视频渲染时的环境。

## Note

代码中的`precondition`和`postcondition`是一种叫做Hoare Triple的技巧的一部分。我借鉴了这一方法以解决长Scene中前后逻辑交错混乱的问题。

配合vscode插件`Better Comments`食用更佳。