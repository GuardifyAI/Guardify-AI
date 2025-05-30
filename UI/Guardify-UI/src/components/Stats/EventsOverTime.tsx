import ChartComponent from './ChartComponent';
import type { Event } from '../../types';

type Props = {
  events: Event[];
  title?: string;
};

export default function EventsOverTime({ events, title = "Events Over Times" }: Props) {
  const eventDates = events.map(e => e.date.slice(0, 10)).sort();
  const uniqueDates = Array.from(new Set(eventDates));
  const eventsPerDay = uniqueDates.map(date =>
    events.filter(e => e.date.startsWith(date)).length
  );

  return (
    <div className="tile">
      <h2>{title}</h2>
    <ChartComponent
      type="line"
      labels={uniqueDates}
      data={eventsPerDay}
      label={title}
    />
    </div>
  );
}
