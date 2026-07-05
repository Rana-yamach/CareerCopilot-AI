interface StreamingTextProps {
  text: string;
  isStreaming?: boolean;
}

/** SSE token akışını gösterir; akış sürerken yanıp sönen bir imleç ekler. */
export function StreamingText({ text, isStreaming }: StreamingTextProps) {
  return (
    <span className="whitespace-pre-wrap break-words">
      {text}
      {isStreaming && (
        <span
          className="ml-0.5 inline-block h-4 w-1.5 animate-pulse align-middle bg-current opacity-70"
          aria-hidden="true"
        />
      )}
    </span>
  );
}
