import ChartComponent from './ChartComponent';

type Props = {
  data: Record<string, number>;
  title?: string;
};

export default function EventCountBarChart({ data, title = "Event Count" }: Props) {
  const labels = Object.keys(data);
  const values = Object.values(data);

  return (
    <div className="tile">
      <ChartComponent
        type="bar"
        labels={labels}
        data={values}
        label={title}
      />
    </div>
  );
}
