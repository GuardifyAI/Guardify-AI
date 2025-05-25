import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

type Event = {
  id: string;
  shopId: string;
  shopName: string;
  date: string;
  description: string;
};

export default function EventsLineChart({ events }: { events: Event[] }) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    const eventDates = events.map(e => e.date.slice(0, 10)).sort();
    const uniqueDates = Array.from(new Set(eventDates));
    const eventsPerDay = uniqueDates.map(date =>
      events.filter(e => e.date.startsWith(date)).length
    );

    if (chartRef.current) {
      if (chartInstance.current) chartInstance.current.destroy();

      chartInstance.current = new Chart(chartRef.current, {
        type: 'line',
        data: {
          labels: uniqueDates,
          datasets: [{
            label: 'Events per Day',
            data: eventsPerDay,
            borderColor: '#30B3E1',
            backgroundColor: 'rgba(48,179,225,0.15)',
            fill: true,
            tension: 0.3,
            pointRadius: 4,
            pointBackgroundColor: '#30B3E1'
          }]
        },
        options: {
          plugins: { legend: { display: false } },
          responsive: true,
          scales: {
            x: { title: { display: true, text: 'Date' } },
            y: { title: { display: true, text: 'Events' }, beginAtZero: true }
          }
        }
      });
    }
  }, [events]);

  return <canvas ref={chartRef} width="300" height="200" />;
}
