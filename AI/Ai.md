# AI相关知识

## train set、dev set和test set的三者联系与区别
    train set：该集合是用于训练模型的。
    dev set：该集合是用于在训练模型中评估模型，以促进模型优化的。
    test set：该集合是用于测试训练好的模型是否有效的。

    简而言之就是：
    你使用了train set训练一个模型，这个模型有一个优化目标，利用dev set来评估你的模型，确定你模型离你的目标差距。在不断迭代中不断用train set训练模型，dev set评估模型，不断靠近你的目标直至最优。之后用test set来验证模型效果。
    注意：dev set 和 test set需要在同一分布下。
