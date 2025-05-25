import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

type Shop = { id: string; name: string; incidents: number; };

export default function ShopsBarChart({ shops }: { shops: Shop[] }) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (chartRef.current) {
      if (chartInstance.current) chartInstance.current.destroy();

      chartInstance.current = new Chart(chartRef.current, {
        type: 'bar',
        data: {
          labels: shops.map(s => s.name),
          datasets: [{
            label: 'Total Events',
            data: shops.map(s => s.incidents),
            backgroundColor: '#30B3E1'
          }]
        },
        options: {
          plugins: { legend: { display: false } },
          responsive: true,
        }
      });
    }
  }, [shops]);

  return <canvas ref={chartRef} width="300" height="200" />;
}
