import ChartComponent from './ChartComponent';

type Props = {
  data: Record<string, number>;
};

export default function EventsByCategory({ data }: Props) {
  const labels = Object.keys(data);
  const values = Object.values(data);

  return (
    <div className="tile">
      <ChartComponent
        type="pie"
        labels={labels}
        data={values}
        label="Events by Category"
      />
    </div>
  );
}
