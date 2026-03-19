import React from 'react';

const ForexSection = ({ data }) => {
  if (!data) return <div>暂无汇率数据</div>;

  // 格式化显示值 - 锁汇成本显示为百分数
  const formatValue = (value, assetName, indicator) => {
    if (assetName === '锁汇成本' && indicator === '锁汇成本') {
      // 转换为百分数并保留2位小数
      return (value * 100).toFixed(2) + '%';
    }
    return Number(value).toFixed(2);
  };

  // 格式化图表数据 - 锁汇成本转换为百分数
  const formatChartData = (priceData, assetName) => {
    if (!priceData || priceData.length === 0) return priceData;

    if (assetName === '锁汇成本') {
      // 将价格转换为百分数
      return priceData.map(item => ({
        ...item,
        price: item.price * 100,
        displayPrice: (item.price * 100).toFixed(2) + '%'
      }));
    }
    return priceData;
  };

  const computeWindowVol = (prices) => {
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
      if (prices[i - 1] !== 0) returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
    }
    if (returns.length < 2) return null;
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + (r - mean) ** 2, 0) / (returns.length - 1);
    return Math.sqrt(variance) * Math.sqrt(252) * 100;
  };

  const calculateAnnualizedVolatility = (priceData) => {
    if (!priceData || priceData.length < 2) return null;
    return computeWindowVol(priceData.map(item => item.price));
  };

  const calculateVolPercentile = (priceSeries3y) => {
    if (!priceSeries3y || priceSeries3y.length < 44) return null;
    const prices = priceSeries3y.map(item => item.price);
    const W = 22;
    const rollingVols = [];
    for (let i = W; i <= prices.length; i++) {
      const vol = computeWindowVol(prices.slice(i - W, i));
      if (vol !== null) rollingVols.push(vol);
    }
    if (rollingVols.length < 2) return null;
    const currentVol = rollingVols[rollingVols.length - 1];
    let count = 0;
    for (const v of rollingVols) { if (v <= currentVol) count++; }
    return { percentile: Math.max(0, Math.min(100, ((count - 1) / (rollingVols.length - 1)) * 100)) };
  };

  const renderPercentileBar = (percentile, current, indicator) => {
    const position = Math.max(0, Math.min(100, percentile));

    return (
      <div className="relative">
        <div className="w-full h-6 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-500 ease-out"
            style={{
              width: `${position}%`,
              background: `linear-gradient(to right, #10B981 0%, #F59E0B 50%, #EF4444 100%)`
            }}
          />
          <div
            className="absolute top-1/2 transform -translate-y-1/2 w-3 h-3 bg-white border-2 border-gray-400 rounded-full shadow-sm"
            style={{ left: `${position}%`, marginLeft: '-6px' }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>便宜</span>
          <span className="font-medium text-gray-700">{position.toFixed(2)}分位</span>
          <span>昂贵</span>
        </div>
      </div>
    );
  };

  const createSimpleTrendChart = (priceData, title, assetName, priceSeries3y) => {
    if (!priceData || priceData.length === 0) {
      return (
        <div className="h-32 flex items-center justify-center text-gray-500">
          暂无走势数据
        </div>
      );
    }

    // 格式化数据以处理锁汇成本的百分数显示
    const formattedData = formatChartData(priceData, assetName);

    // 计算价格变化
    const prices = formattedData.map(item => item.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice || 0.01; // 防止除零错误

    // 生成SVG路径
    const width = 300;
    const height = 150;
    const padding = 20;

    const points = formattedData.map((item, index) => {
      const x = padding + (index / (formattedData.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((item.price - minPrice) / priceRange) * (height - 2 * padding);
      return `${x},${y}`;
    }).join(' ');

    const currentPrice = prices[prices.length - 1];
    const firstPrice = prices[0];
    const change = ((currentPrice - firstPrice) / firstPrice) * 100;
    const isPositive = change >= 0;

    return (
      <div className="h-32">
        <div className="mb-1 text-right">
          <span className={`text-xs font-medium ${isPositive ? 'text-red-600' : 'text-green-600'}`}>
            {isPositive ? '+' : ''}{change.toFixed(2)}%
          </span>
        </div>
        <svg width="100%" height="100" viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
          {/* 网格线 */}
          <defs>
            <pattern id="grid-forex" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f3f4f6" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid-forex)" />

          {/* 价格线 */}
          <polyline
            fill="none"
            stroke="#8B5CF6"
            strokeWidth="2"
            points={points}
          />

          {/* 填充区域 */}
          <polygon
            fill="rgba(139, 92, 246, 0.1)"
            points={`${padding},${height - padding} ${points} ${width - padding},${height - padding}`}
          />

          {/* 数据点 */}
          {formattedData.map((item, index) => {
            const x = padding + (index / (formattedData.length - 1)) * (width - 2 * padding);
            const y = height - padding - ((item.price - minPrice) / priceRange) * (height - 2 * padding);
            const displayValue = item.displayPrice || item.price;
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="3"
                fill="#8B5CF6"
                className="opacity-0 hover:opacity-100 transition-opacity"
              >
                <title>{`${item.date}: ${displayValue}`}</title>
              </circle>
            );
          })}
        </svg>

        {/* X轴标签 */}
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{formattedData[0]?.date}</span>
          <span>{formattedData[formattedData.length - 1]?.date}</span>
        </div>

        {/* 近1月年化波动率 & 近3年分位数 */}
        {(() => {
          const vol = calculateAnnualizedVolatility(priceData);
          if (vol === null) return null;
          const volColor = vol < 5
            ? 'text-green-700 bg-green-50 border-green-200'
            : vol < 15
              ? 'text-amber-700 bg-amber-50 border-amber-200'
              : 'text-red-700 bg-red-50 border-red-200';
          const volStats = calculateVolPercentile(priceSeries3y);
          const pos = volStats ? Math.max(0, Math.min(100, volStats.percentile)) : null;
          return (
            <div className="mt-2 pt-1.5 border-t border-gray-100">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <span className="text-[11px] font-bold text-gray-400 leading-none">σ</span>
                  近1月年化波动率
                </span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${volColor}`}>
                  {vol.toFixed(2)}%
                </span>
              </div>
              {pos !== null && (
                <div className="mt-1.5">
                  <div className="relative">
                    <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full" style={{ width: `${pos}%`, background: 'linear-gradient(to right, #10B981 0%, #F59E0B 50%, #EF4444 100%)' }} />
                    </div>
                    <div className="absolute top-1/2 transform -translate-y-1/2 w-2.5 h-2.5 bg-white border-2 border-gray-400 rounded-full shadow-sm" style={{ left: `${pos}%`, marginLeft: '-5px' }} />
                  </div>
                  <div className="flex justify-between text-[9px] text-gray-400 mt-0.5">
                    <span>低波动</span>
                    <span className="font-medium text-gray-500">{pos.toFixed(1)}分位 · 近3年</span>
                    <span>高波动</span>
                  </div>
                </div>
              )}
            </div>
          );
        })()}
      </div>
    );
  };

  const renderAssetCard = (assetName, assetData) => {
    if (!assetData || !assetData.indicators) return null;

    return (
      <div key={assetName} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* 左侧：指标数据 */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
              <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2"></span>
              {assetName}
            </h3>

            <div className="space-y-2">
              {assetData.indicators.map((indicator, index) => (
                <div key={index} className="bg-white rounded-md p-2 shadow-sm">
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900">{indicator.indicator}</span>
                      {indicator.vs_median > 0 ? (
                        <svg className="w-3 h-3 text-red-500 ml-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg className="w-3 h-3 text-green-500 ml-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <span className="text-sm font-bold text-gray-900">{formatValue(indicator.current, assetName, indicator.indicator)}</span>
                  </div>

                  {renderPercentileBar(indicator.percentile, indicator.current, indicator.indicator)}
                </div>
              ))}
            </div>
          </div>

          {/* 右侧：走势图 */}
          <div>
            <div className="bg-white rounded-md p-2 shadow-sm h-full">
              <h4 className="text-xs font-medium text-gray-700 mb-1">近一个月走势</h4>
              <div className="text-xs text-gray-500 mb-1">{assetName}</div>
              {createSimpleTrendChart(assetData.price_series, assetName, assetName, assetData.price_series_3y)}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // 定义显示顺序 - 确保USDCNY在锁汇成本之前
  const assetOrder = ['USDCNY', '锁汇成本'];

  // 按指定顺序排序，其他资产放在最后
  const sortedEntries = Object.entries(data).sort(([a], [b]) => {
    const indexA = assetOrder.indexOf(a);
    const indexB = assetOrder.indexOf(b);

    // 如果两个都在排序数组中，按数组顺序排
    if (indexA !== -1 && indexB !== -1) {
      return indexA - indexB;
    }
    // 如果只有一个在排序数组中，优先显示在排序数组中的
    if (indexA !== -1) return -1;
    if (indexB !== -1) return 1;
    // 如果都不在排序数组中，按字母顺序排
    return a.localeCompare(b);
  });

  return (
    <div className="space-y-3">
      {sortedEntries.map(([assetName, assetData]) =>
        renderAssetCard(assetName, assetData)
      )}
    </div>
  );
};

export default ForexSection;

