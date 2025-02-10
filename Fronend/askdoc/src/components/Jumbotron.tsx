const Jumbotron = () => {
  return (
    <div className="bg-gradient-to-r from-blue-500/30 to-purple-500/30 py-20 rounded-lg">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-5xl font-medium mb-4">Chat with Your Documents</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Upload your PDFs and get instant answers to your questions using AI.
          Simple, fast, and accurate document interaction.
        </p>
      </div>
    </div>
  );
};

const MiniJumbotron = () => {
  return (
    <div className="bg-gradient-to-r from-blue-500/30 to-purple-500/30 mb-4 py-5 rounded-lg">
      <div className="container mx-auto px-4 text-center">
        <p className="text-xl mx-auto max-w-4xl font-light font-medium">
          You can now initiate a
          <span className="font-semibold"> Chat with Your Documents</span>,
          enabling seamless interaction and efficient information retrieval
          directly within the conversation.
        </p>
      </div>
    </div>
  );
};

export { Jumbotron, MiniJumbotron };
