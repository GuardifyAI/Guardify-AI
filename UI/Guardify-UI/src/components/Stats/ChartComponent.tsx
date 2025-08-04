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

  // Professional color palette for charts
  const pieColors = [
    '#30B3E1', '#0288d1', '#0277bd', '#0369a1',
    '#075985', '#0c4a6e', '#ef4444', '#dc2626'
  ];

  const gradientColors = [
    '#30B3E1', '#10b981', '#f59e0b', '#ef4444',
    '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
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
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              display: isPie, 
              position: 'bottom',
              labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                  size: 12,
                  family: 'Inter, sans-serif'
                }
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: '#ffffff',
              bodyColor: '#ffffff',
              borderColor: '#30B3E1',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: true,
              font: {
                family: 'Inter, sans-serif'
              }
            }
          },
          scales: isPie ? {} : {
            x: {
              title: {
                display: true,
                text: isHorizontal ? 'Events Count' : (type === 'bar' ? 'Category' : 'Date'),
                font: {
                  size: 12,
                  family: 'Inter, sans-serif',
                  weight: '500'
                },
                color: '#64748b'
              },
              grid: {
                color: '#f1f5f9',
                borderColor: '#e2e8f0'
              },
              ticks: {
                font: {
                  size: 11,
                  family: 'Inter, sans-serif'
                },
                color: '#64748b'
              }
            },
            y: {
              title: {
                display: true,
                text: isHorizontal ? 'Camera Name' : 'Count',
                font: {
                  size: 12,
                  family: 'Inter, sans-serif',
                  weight: '500'
                },
                color: '#64748b'
              },
              beginAtZero: true,
              grid: {
                color: '#f1f5f9',
                borderColor: '#e2e8f0'
              },
              ticks: {
                font: {
                  size: 11,
                  family: 'Inter, sans-serif'
                },
                color: '#64748b'
              }
            }
          },
          indexAxis: isHorizontal ? 'y' : 'x',
          elements: {
            bar: {
              borderRadius: 4,
              borderSkipped: false,
            },
            point: {
              radius: 4,
              hoverRadius: 6
            },
            line: {
              tension: 0.4
            }
          }
        }
      });
    }
  }, [type, labels, data, label, color]);

return (
  <div className={`${type === 'pie' ? 'h-64' : 'h-64'} w-full`}>
    <canvas
      ref={chartRef}
      className="w-full h-full"
    />
  </div>
);
}