import ChartComponent from './ChartComponent';

type Props = {
  data: Record<string, number>;
};

export default function EventsOverTime({ data }: Props) {
  // Convert stats data to chart format and sort by date
  const chartData = Object.entries(data)
    .map(([date, count]) => ({
      date,
      count
    }))
    .sort((a, b) => a.date.localeCompare(b.date));

  return (
    <div className="tile">
      <ChartComponent
        label="Events Over Time"
        type="line"
        labels={chartData.map(d => d.date)}
        data={chartData.map(d => d.count)}
      />
    </div>
  );
}
