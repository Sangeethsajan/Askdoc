const LoadingDots = () => {
  return (
    <div className="flex space-x-1 justify-center items-center h-3">
      <div className="w-1 h-1 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-1 h-1 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-1 h-1 bg-current rounded-full animate-bounce"></div>
    </div>
  );
};

export default LoadingDots;
