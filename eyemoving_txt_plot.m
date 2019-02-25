filename = '.\record_19_02_25_12_40_39-12_41_35\record_left_eye_19_02_25_12_40_39-12_41_35.txt';

data=importdata(filename);

%将样机采集数据保存到matlab中的矩阵中
DATA=zeros(length(data),2);
for i=1 : length(data)
    
   new=data{i,1} ;%从cell中取出字符
   new_data=str2num(new);%将字符转换成数组
   
   DATA(i,1)=new_data(1);
   DATA(i,2)=new_data(2);%将数组填充进之前建立的矩阵中，第一列为眼动的x，第二列为眼动的y
    
end

%绘制轨线图
figure(1)
plot(DATA(:,1),DATA(:,2),'-*')
grid on
ha=gca;
set(ha,'xlim',[-1,1])
set(ha,'ylim',[-1,1])
title('Eye moving trajectory diagram')
%计算最佳时延

%--------------------------------------------------------------------------
% 调用 mex 函数
X=DATA(:,2);

maxLags = 50;          % 最大时延
Part = 20;             % 每一座标划分的份数
r = Amutual_lzb(X,maxLags,Part);

%--------------------------------------------------------------------------
% 寻找第一个局部极小点

tau = [];
for i = 1:length(r)-1           
    if (r(i)<=r(i+1))
        tau = i;            % 第一个局部极小值位置
        break;
    end
end
if isempty(tau)
    tau = length(r);
end
optimal_tau = tau -1    % r 的第一个值对应 tau = 0,所以要减 1

%--------------------------------------------------------------------------
% 图形显示
figure(2)
plot(0:length(r)-1,r,'.-')
xlabel('Lag');
title('互信息法求时延X');







