interface ErrorDisplayProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  fullScreen?: boolean;
}

export default function ErrorDisplay({ 
  title = "Error", 
  message, 
  onRetry, 
  fullScreen = false 
}: ErrorDisplayProps) {
  const containerClass = fullScreen 
    ? "min-h-screen bg-gray-50 flex items-center justify-center"
    : "bg-red-50 border border-red-200 rounded-lg p-6 mb-6";

  return (
    <div className={containerClass}>
      <div className="text-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-red-800 font-semibold mb-2">{title}</h3>
          <p className="text-red-600 mb-4">{message}</p>
          {onRetry && (
            <button 
              onClick={onRetry}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
