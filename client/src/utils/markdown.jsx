import React from 'react';

const parseInline = (text) => {
  // Split on bold segments (**text**)
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-violet-400">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
};

export const renderMarkdown = (text) => {
  if (!text) return null;
  
  const lines = text.split('\n');
  
  return (
    <div className="space-y-1 text-gray-200">
      {lines.map((line, idx) => {
        const content = line.trim();
        if (!content) return <div key={idx} className="h-1.5" />;
        
        // Headings
        if (content.startsWith('# ')) {
          return <h1 key={idx} className="text-lg font-bold text-white mt-3 mb-1.5">{parseInline(content.slice(2))}</h1>;
        }
        if (content.startsWith('## ')) {
          return <h2 key={idx} className="text-md font-bold text-white mt-2.5 mb-1.5">{parseInline(content.slice(3))}</h2>;
        }
        if (content.startsWith('### ')) {
          return <h3 key={idx} className="text-sm font-bold text-white mt-2 mb-1">{parseInline(content.slice(4))}</h3>;
        }
        
        // Bullet Lists
        if (content.startsWith('- ') || content.startsWith('* ')) {
          return (
            <ul key={idx} className="list-disc pl-5 my-0.5 text-gray-300">
              <li className="text-sm leading-relaxed">{parseInline(content.slice(2))}</li>
            </ul>
          );
        }
        
        // Numbered Lists
        const numListMatch = content.match(/^(\d+)\.\s(.*)/);
        if (numListMatch) {
          return (
            <ol key={idx} className="list-decimal pl-5 my-0.5 text-gray-300" start={numListMatch[1]}>
              <li className="text-sm leading-relaxed">{parseInline(numListMatch[2])}</li>
            </ol>
          );
        }
        
        // Default Paragraph
        return <p key={idx} className="text-sm leading-relaxed my-0.5">{parseInline(content)}</p>;
      })}
    </div>
  );
};
