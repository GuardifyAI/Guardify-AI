import ChartComponent from './ChartComponent';
import type { Event } from '../../types';

type Props = {
  events?: Event[];
  groupBy: 'shopId' | 'camera';
  title?: string;
};

export default function EventCountBarChart({ events, groupBy }: Props) {
  if (!events || !Array.isArray(events)) {
    return <div className="tile">No event data</div>;
  }

  const counts: Record<string, number> = {};

  events.forEach(event => {
    const key =
      groupBy === 'camera'
        ? event.cameraName || event.cameraId
        : groupBy === 'shopId'
          ? event.shopName || event.shopId
          : event[groupBy];
    counts[key] = (counts[key] || 0) + 1;
  });

  const labels = Object.keys(counts);
  const data = labels.map(label => counts[label]);

  return (
    <div className="tile">
      <h2>{`Events by ${groupBy}`}</h2>
      <ChartComponent
        type="bar"
        labels={labels}
        data={data}
        label={`Events by ${groupBy}`}
      />
    </div>
  );
}
