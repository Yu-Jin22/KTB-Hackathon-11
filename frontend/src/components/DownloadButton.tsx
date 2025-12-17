import React, { useState } from 'react';
import { Download, FileText, File, ChevronDown } from 'lucide-react';
import { downloadExport } from '../api/fastApi';

interface DownloadButtonProps {
  jobId: string | null;
  disabled: boolean;
  recipeTitle?: string;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({ jobId, disabled, recipeTitle }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async (format: 'markdown' | 'pdf') => {
    if (!jobId) return;

    setIsDownloading(true);
    try {
      const blob = await downloadExport(jobId, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${recipeTitle || 'recipe'}.${format === 'markdown' ? 'md' : 'pdf'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('다운로드 중 오류가 발생했습니다.');
    } finally {
      setIsDownloading(false);
      setIsOpen(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled || isDownloading}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
          ${disabled
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-primary-500 text-white hover:bg-primary-600 shadow-md hover:shadow-lg'
          }
        `}
      >
        {isDownloading ? (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
        ) : (
          <Download className="w-5 h-5" />
        )}
        <span>다운로드</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && !disabled && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-10">
          <button
            onClick={() => handleDownload('pdf')}
            className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
          >
            <File className="w-5 h-5 text-red-500" />
            <div className="text-left">
              <div className="font-medium text-gray-800">PDF</div>
              <div className="text-xs text-gray-500">이미지 포함</div>
            </div>
          </button>
          <button
            onClick={() => handleDownload('markdown')}
            className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
          >
            <FileText className="w-5 h-5 text-blue-500" />
            <div className="text-left">
              <div className="font-medium text-gray-800">Markdown</div>
              <div className="text-xs text-gray-500">텍스트 기반</div>
            </div>
          </button>
        </div>
      )}

      {/* 드롭다운 외부 클릭 시 닫기 */}
      {isOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default DownloadButton;
