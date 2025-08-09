/**
 * Clean up error messages to be more user-friendly
 * @param message The error message to clean
 */
export function cleanErrorMessage(message?: string): string {
  if (!message) return 'An error occurred';

  const patterns = [
    /^HTTP\s*\d+:\s*/i,
    /^\d+\s*:\s*/,
    /^\d+\s+[A-Za-z\s]+:\s*/i,
    /^Error:\s*/i,
    /^Exception:\s*/i,
    /^Unauthorized:\s*/i,
    /^Bad\s+Request:\s*/i,
    /^Internal\s+Server\s+Error:\s*/i
  ];

  let cleanMessage = message.trim();
  for (const pattern of patterns) {
    cleanMessage = cleanMessage.replace(pattern, '');
  }

  cleanMessage = cleanMessage.trim();
  return cleanMessage
    ? cleanMessage.charAt(0).toUpperCase() + cleanMessage.slice(1)
    : 'An error occurred';
}