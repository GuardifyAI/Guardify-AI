import ChartComponent from './ChartComponent';
import type { Event } from '../../types';

type Props = {
  events: Event[];
  groupBy: 'shopId' | 'cameraId';
  title?: string;
};

export default function EventCountBarChart({ events, groupBy, title }: Props) {
  const counts: Record<string, number> = {};

  events.forEach(event => {
    const key = event[groupBy];
    counts[key] = (counts[key] || 0) + 1;
  });

  const labels = Object.keys(counts);
  const data = labels.map(label => counts[label]);

  return (
    <div className="tile">
      <h2>{title || `Events by ${groupBy}`}</h2>
      <ChartComponent
        type="bar"
        labels={labels}
        data={data}
        label={`Events per ${groupBy}`}
      />
    </div>
  );
}
