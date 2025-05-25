import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import type { Event } from '../types';

type Props = {
  events: Event[];
};

export default function CameraStats({ events }: Props) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    const cameraCounts: Record<string, number> = {};

    events.forEach(event => {
      const key = event.cameraName;
      cameraCounts[key] = (cameraCounts[key] || 0) + 1;
    });

    const labels = Object.keys(cameraCounts);
    const data = Object.values(cameraCounts);

    if (chartRef.current) {
      if (chartInstance.current) chartInstance.current.destroy();

      chartInstance.current = new Chart(chartRef.current, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Events by Camera',
            data,
            backgroundColor: '#30B3E1'
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              title: { display: true, text: 'Camera' }
            },
            y: {
              title: { display: true, text: 'Events' },
              beginAtZero: true
            }
          }
        }
      });
    }
  }, [events]);

  return (
    <div className="tile">
      <h2>Events by Camera</h2>
      <canvas ref={chartRef} width="300" height="200"></canvas>
    </div>
  );
}
