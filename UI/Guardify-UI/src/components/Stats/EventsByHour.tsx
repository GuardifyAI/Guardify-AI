import ChartComponent from './ChartComponent';
import type { Event } from '../../types';

type Props = {
  events: Event[];
  title?: string;
};

export default function EventsByHour({ events }: Props) {
  const hoursCount = new Array(24).fill(0);

  events.forEach(event => {
    const hour = new Date(event.date).getHours();
    hoursCount[hour]++;
  });

  const data = hoursCount.map((count, hour) => ({
    hour: `${hour}:00`,
    count
  }));

  return (
    <div className="tile">
      <ChartComponent
        label="Events by Hour"
        type="bar"
        labels={data.map(d => d.hour)}
        data={data.map(d => d.count)}
      />
    </div>
  );
}
