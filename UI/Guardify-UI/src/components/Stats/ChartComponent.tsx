import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

type ChartProps = {
  type: 'bar' | 'line' | 'pie';
  labels: string[];
  data: number[];
  label: string;
  color?: string;
  horizontal?: boolean;
};

export default function ChartComponent({
  type,
  labels,
  data,
  label,
  color = '#30B3E1',
  horizontal
}: ChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  // Blue shades for pie chart segments
  const pieColors = [
    '#b3e5fc', '#81d4fa', '#4fc3f7', '#29b6f6',
    '#03a9f4', '#039be5', '#0288d1', '#0277bd'
  ];

  useEffect(() => {
    if (chartRef.current) {
      if (chartInstance.current) chartInstance.current.destroy();

      const isPie = type === 'pie';
      const isHorizontal = horizontal && type === 'bar';

      chartInstance.current = new Chart(chartRef.current, {
        type,
        data: {
          labels,
          datasets: [{
            label,
            data,
            backgroundColor: isPie
              ? pieColors.slice(0, labels.length)
              : (type === 'bar' ? color : `${color}22`),
            borderColor: isPie ? 'white' : color,
            borderWidth: isPie ? 1 : 2,
            fill: type === 'line',
            tension: type === 'line' ? 0.3 : 0,
            pointRadius: type === 'line' ? 4 : 0,
            pointBackgroundColor: color,
          }]
        },
        options: {
          responsive: true,
        plugins: {
          legend: { display: isPie, position: 'bottom' }
        },
          scales: isPie ? {} : {
        x: {
          title: {
            display: true,
            text: isHorizontal ? 'Events Count' : (type === 'bar' ? 'Category' : 'Date')
          }
        },
        y: {
          title: {
            display: true,
            text: isHorizontal ? 'Camera Name' : 'Count'
          },
          beginAtZero: true
        }
          },
          indexAxis: isHorizontal ? 'y' : 'x',
        }
      });
    }
  }, [type, labels, data, label, color]);

return (
  <canvas
    ref={chartRef}
    width={type === 'pie' ? 220 : 300}
    height={type === 'pie' ? 220 : 200}
  />
);
}