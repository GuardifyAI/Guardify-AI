import type { Event } from '../../types';
import ChartComponent from './ChartComponent';

type Props = {
  events: Event[];
};

export default function EventsByCategory({ events }: Props) {
  const categories: Record<string, string[]> = {
    'Security': ['suspicious', 'shoplifting', 'unusual', 'alert', 'rush'],
    'Shelf Interaction': ['shelf', 'taking', 'item', 'product', 'grab'],
    'Cash / Register': ['cash', 'register', 'checkout', 'kupa', 'payment'],
  };

  const counts: Record<string, number> = {};
  Object.keys(categories).forEach(c => (counts[c] = 0));
  counts['Other'] = 0;

  events.forEach(event => {
    const desc = event.description.toLowerCase();
    let bestCategory = 'Other';
    let maxMatches = 0;

    for (const [category, keywords] of Object.entries(categories)) {
      const matches = keywords.filter(k => desc.includes(k)).length;
      if (matches > maxMatches) {
        maxMatches = matches;
        bestCategory = category;
      }
    }

    counts[bestCategory]++;
  });

  const labels = Object.keys(counts);
  const data = labels.map(label => counts[label]);

  return (
    <div className="tile">
      <ChartComponent
        type="pie"
        labels={labels}
        data={data}
        label="Events by Category"
      />
    </div>
  );
}
