# 光的偏振与马吕斯定律 —— 课堂讲义（第 3 章）

## 3.1 偏振态的描述

自然光在垂直于传播方向的平面上各方向振动，可分解为两个正交分量。
线偏振光的偏振方向由 Jones 矢量描述：

$$
\mathbf{E} = E_0 \begin{pmatrix} \cos\theta \\ \sin\theta \end{pmatrix}
$$

其中 $E_0$ 是振幅，$\theta$ 是偏振角。当 $\theta = 0$ 时为水平偏振。

未偏振光可用 Stokes 参数描述，四分之一偏振度记作 $D = \frac{S_1}{S_0}$。
注意本讲义的公式一律写成纯文本，可直接复制进 Word 或报告；带 `·` 的是乘号。

## 3.2 马吕斯定律

当线偏振光通过检偏器时，透射光强为：

$$
I = I_0 \cos^2\theta
$$

对应的纯文本写法是 I = I₀ cos²θ，阻尼项有时也写成 exp(-γt)。

两个偏振片夹在一起时，强度比满足 $I/I_0 = \cos^2\theta$。
若第一片的偏振角是 θ₁ 而第二片是 θ₂，则 Malus 定律给出：

$$
I = I_0 \cos^2(\theta_2 - \theta_1)
$$

旋光率为 $\alpha = \frac{\pi}{\lambda}\Delta n$，旋光角 $\varphi = \alpha l$。

## 3.3 双折射与波片

方解石晶体对 o 光和 e 光有不同折射率，产生双折射：

$$
\Delta n = n_e - n_o
$$

相位延迟为 $\delta = \frac{2\pi}{\lambda} \Delta n \cdot d$，其中 d 是晶体厚度。
当 $\delta = \pi/2$ 时称为四分之一波片，此时输出为圆偏振光。

光程差可写成 Δ = d(n_e − n_o)。

## 3.4 菲涅耳公式

界面反射的振幅系数为：

$$
r_{s} = \frac{n_1 \cos\theta_i - n_2 \cos\theta_t}{n_1 \cos\theta_i + n_2 \cos\theta_t}
$$

$$
r_{p} = \frac{n_2 \cos\theta_i - n_1 \cos\theta_t}{n_2 \cos\theta_i + n_1 \cos\theta_t}
$$

反射率为 $R = |r|^2$，其中 |r| 表示模。

## 3.5 仪器与单位

强度单位是 W/m²，消光比用 dB 表示，偏振度的单位是 %。
波长单位 nm，折射率无量纲，角度用 ° 或 rad。
角速度单位 rad/s，曝光时间单位 ms。

## 3.6 数据处理示例

下面这段是 Python 代码，变量名不要动：

```python
import numpy as np
from scipy.optimize import curve_fit

def malus(I0, theta):
    return I0 * np.cos(np.deg2rad(theta))**2

I0_hat, _ = curve_fit(malus, data_x, data_y)
omega_0 = 2 * np.pi * freq
```

拟合得到的 I0_hat 与理论值 3.2 W/m² 相差约 5%。
相对误差定义为 δ_rel = |I0_meas - I0_fit| / I0_fit。
