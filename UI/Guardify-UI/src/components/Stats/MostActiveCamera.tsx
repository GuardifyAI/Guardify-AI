import ChartComponent from './ChartComponent';
import type { Event } from '../../types';

type Props = {
  events: Event[];
  title?: string;
};

export default function MostActiveCamera({ events, title = "Events by Camera" }: Props) {
  const cameraCounts: Record<string, number> = {};

  events.forEach(event => {
    cameraCounts[event.cameraId] = (cameraCounts[event.cameraId] || 0) + 1;
  });

  const labels = Object.keys(cameraCounts);
  const data = labels.map(label => cameraCounts[label]);

  return (
    <div className="tile">
      <h2>{title}</h2>
      <ChartComponent
        type="bar"
        labels={labels}
        data={data}
        label="Events per Camera"
        horizontal
      />
    </div>
  );
}
