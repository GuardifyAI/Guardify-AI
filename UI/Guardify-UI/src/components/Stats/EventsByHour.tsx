import ChartComponent from './ChartComponent';

type Props = {
  data: Record<string, number>;
};

export default function EventsByHour({ data }: Props) {
  // Convert stats data to chart format
  const chartData = Object.entries(data)
    .map(([hour, count]) => ({
      hour: `${hour.padStart(2, '0')}:00`,
      count
    }))
    .sort((a, b) => a.hour.localeCompare(b.hour));

  return (
    <div className="tile">
      <ChartComponent
        label="Events by Hour"
        type="bar"
        labels={chartData.map(d => d.hour)}
        data={chartData.map(d => d.count)}
      />
    </div>
  );
}
