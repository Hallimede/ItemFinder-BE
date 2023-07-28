import numpy as np
import matplotlib.pyplot as plt
import librosa.display
import soundfile as sf

# 音频文件所在路径
audio_path = 'audio_test2.wav'

# 加载文件为ndarray格式
x, sr = librosa.load(audio_path, sr=None)
# sr为音频采样率， 设为None即采用原采样率，不写则默认使用22.05khz采样

# plt.subplot(311)
# librosa.display.waveplot(x, sr=sr)

# 定义x的初始状态

x_mat = np.mat([0])
print("【x_mat】")
print(x_mat)
# 定义初始状态协方差矩阵

p_mat = np.mat([10])
print("【p_mat】")
print(p_mat)

# 定义状态转移矩阵，因为每秒钟采一次样，所以delta_t = 1
f_mat = np.mat([1])

# 定义状态转移协方差矩阵，这里我们把协方差设置的很小，因为觉得状态转移矩阵准确度高
q_mat = np.mat([0.00001])

# 定义观测矩阵
h_mat = np.mat([1])

# 定义观测噪声协方差
r_mat = np.mat([0.001])

noise = np.round(np.random.normal(0, 0.005, len(x)), 2)

for i in range(0, len(x)):
    # 创建一个方差为1的高斯噪声，精确到小数点后两位
    x[i] += noise[i]

sf.write('stereo_file2.wav', x, samplerate=sr, subtype='PCM_24')
plt.subplot(211)
librosa.display.waveplot(x, sr=sr)

for i in range(0, len(x)):
    x_predict = f_mat * x_mat
    p_predict = f_mat * p_mat * f_mat.T + q_mat
    kalman = p_predict * h_mat.T / (h_mat * p_predict * h_mat.T + r_mat)
    x_mat = x_predict + kalman * (x[i] - h_mat * x_predict)
    p_mat = (1 - kalman * h_mat) * p_predict
    x[i] = x_mat

sf.write('stereo_file3.wav', x, samplerate=sr, subtype='PCM_24')
# 设置画布大小
plt.subplot(212)
# 调用librosa包画出波形图
librosa.display.waveplot(x, sr=sr)

# 设置画布标题
# plt.title('sound wave')

plt.ylabel("amlitude")
plt.xlabel("time")
# 显示画布
plt.show()
