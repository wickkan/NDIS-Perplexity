'use client';

import { Button } from '@/components/ui/button';
import {
  FileUpload,
  FileUploadDropzone,
  FileUploadItem,
  FileUploadItemDelete,
  FileUploadItemMetadata,
  FileUploadItemPreview,
  FileUploadItemProgress,
  FileUploadList,
} from '@/components/ui/file-upload';
import { Textarea } from '@/components/ui/textarea';
import { fetchFromEndpoint } from '@/lib/api';
import { ENDPOINTS } from '@/lib/constants';
import { cn } from '@/lib/utils';
import { ArrowUp, Upload, X } from 'lucide-react';
import { ChangeEvent, FormEvent, useCallback, useState } from 'react';
import { toast } from 'sonner';
import { ShineBorder } from './magicui/shine-border';
import ResultsDisplay from './results';
import { Label } from './ui/label';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';

export default function InvoiceChat() {
  const [input, setInput] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedApi, setSelectedApi] = useState(ENDPOINTS.DECODE.url);
  const [response, setResponse] = useState<any>(null);

  const onInputChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>) => {
      setInput(event.target.value);
    },
    []
  );

  const onKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Submit on Enter without Shift key
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (input.trim() && !isUploading && !isLoading) {
          const form = event.currentTarget.closest('form') as HTMLFormElement;
          if (form) {
            // Use the form.submit() method to submit the form
            form.requestSubmit();
          }
        }
      }
    },
    [input, isUploading, isLoading]
  );

  const onUpload = useCallback(
    async (
      files: File[],
      {
        onProgress,
        onSuccess,
        onError,
      }: {
        onProgress: (file: File, progress: number) => void;
        onSuccess: (file: File) => void;
        onError: (file: File, error: Error) => void;
      }
    ) => {
      try {
        setIsUploading(true);
        // Process each file individually
        const uploadPromises = files.map(async (file) => {
          try {
            // Simulate file upload with progress
            const totalChunks = 10;
            let uploadedChunks = 0;

            // Simulate chunk upload with delays
            for (let i = 0; i < totalChunks; i++) {
              // Simulate network delay (100-300ms per chunk)
              await new Promise((resolve) =>
                setTimeout(resolve, Math.random() * 200 + 100)
              );

              // Update progress for this specific file
              uploadedChunks++;
              const progress = (uploadedChunks / totalChunks) * 100;
              onProgress(file, progress);
            }

            // Simulate server processing delay
            await new Promise((resolve) => setTimeout(resolve, 500));
            onSuccess(file);
          } catch (error) {
            onError(
              file,
              error instanceof Error ? error : new Error('Upload failed')
            );
          } finally {
            setIsUploading(false);
          }
        });

        // Wait for all uploads to complete
        await Promise.all(uploadPromises);
      } catch (error) {
        // This handles any error that might occur outside the individual upload processes
        console.error('Unexpected error during upload:', error);
      }
    },
    []
  );

  const onFileReject = useCallback((file: File, message: string) => {
    toast(message, {
      description: `"${
        file.name.length > 20 ? `${file.name.slice(0, 20)}...` : file.name
      }" has been rejected`,
    });
  }, []);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    try {
      event.preventDefault();
      
      // Don't submit if already loading or empty input
      if (isLoading || !input.trim()) {
        return;
      }
      
      setIsLoading(true);
      
      // Special handling for Budget Planning Assistant
      if (selectedApi === '/api/plan-budget') {
        // Try to extract plan amount from input
        // Look for patterns like "$50000" or "50,000" or "50k" in the input
        const amountRegex = /\$(\d[\d,]*\.?\d*\s*k?)|\b(\d[\d,]*\.?\d*\s*k?)\s*dollars\b|(\d[\d,]*\.?\d*\s*k?)\b/i;
        const match = input.match(amountRegex);
        
        let planAmount = 0;
        if (match) {
          // Extract the amount part, remove commas, handle 'k' for thousands
          let extractedAmount = match[0].replace(/[\$,\s]/g, '');
          if (extractedAmount.toLowerCase().endsWith('k')) {
            extractedAmount = extractedAmount.toLowerCase().replace('k', '') + '000';
          }
          planAmount = parseFloat(extractedAmount);
        }
        
        if (!planAmount || planAmount <= 0) {
          setResponse({
            error: 'Invalid plan amount',
            message: 'Please include a valid NDIS plan amount in your query, for example: "Help me allocate my $50,000 NDIS plan"',
            status: 'error'
          });
          setIsLoading(false);
          return;
        }
        
        try {
          const res = await fetchFromEndpoint(
            selectedApi,
            JSON.stringify({
              plan_amount: planAmount,
              needs_description: input,
              existing_supports: [],
              priorities: []
            }),
            undefined
          );
          
          console.log(res);
          setResponse(res);
          setInput('');
          setFiles([]);
        } catch (error) {
          console.error('Error fetching from budget endpoint:', error);
          setResponse({
            error: 'Request failed',
            message: 'There was an error processing your request. Please try again.',
            status: 'error'
          });
        }
      } else {
        // Standard handling for other endpoints
        try {
          const res = await fetchFromEndpoint(
            selectedApi,
            JSON.stringify({ query: input }),
            undefined
          );
          
          console.log(res);
          setResponse(res);
          setInput('');
          setFiles([]);
        } catch (error) {
          console.error('Error fetching from endpoint:', error);
          setResponse({
            error: 'Request failed',
            message: 'There was an error processing your request. Please try again.',
            status: 'error'
          });
        }
      }
      
      // Always set loading to false at the end
      setIsLoading(false);
    } catch (err) {
      console.error('Form submission error:', err);
      setIsLoading(false);
      setResponse({
        error: 'Submission error',
        message: 'There was an error submitting your request. Please try again.',
        status: 'error'
      });
    }
  };

  return (
    <>
      <RadioGroup
        defaultValue={selectedApi}
        className="sm:grid-cols-2"
        onValueChange={(value) => {
          setResponse('');
          setSelectedApi(value);
        }}
      >
        {Object.entries(ENDPOINTS).map(
          ([_, { name, description, url }], index) => (
            <div
              className="flex items-center space-x-2 p-4 border rounded col-span-1"
              key={index}
            >
              <RadioGroupItem value={url} id={`api-${url}`} />
              <Label htmlFor={`api-${url}`} className="font-bold">
                {name}{' '}
                <p className="text-slate-600 font-normal mt-1 opacity-75">
                  {description}
                </p>
              </Label>
            </div>
          )
        )}
      </RadioGroup>

      <FileUpload
        value={files}
        onValueChange={setFiles}
        onUpload={onUpload}
        onFileReject={onFileReject}
        maxFiles={10}
        maxSize={5 * 1024 * 1024}
        className="relative w-full"
        multiple
        disabled={isUploading}
      >
        <FileUploadDropzone
          tabIndex={-1}
          // Prevents the dropzone from triggering on click
          onClick={(event) => event.preventDefault()}
          className="absolute inset-0 z-0 flex w-full items-center justify-center rounded-none border-none bg-background/50 p-0 opacity-0 backdrop-blur transition-opacity duration-200 ease-out data-[dragging]:z-10 data-[dragging]:opacity-100"
        >
          <div className="flex flex-col items-center gap-1 text-center">
            <div className="flex items-center justify-center rounded-full border p-2.5">
              <Upload className="size-6 text-muted-foreground" />
            </div>
            <p className="font-medium text-sm">Drag & drop files here</p>
            <p className="text-muted-foreground text-xs">
              Upload max 5 files each up to 5MB
            </p>
          </div>
        </FileUploadDropzone>
        <form
          onSubmit={onSubmit}
          className={cn(
            'relative flex w-full flex-col gap-2.5 rounded-md px-3 py-2 outline-none focus-within:ring-1 focus-within:ring-ring/50 border',
            isUploading || isLoading
              ? 'border-transparent focus-within:ring-ring/10'
              : 'border-input'
          )}
        >
          {isUploading || isLoading ? (
            <ShineBorder shineColor={['#A07CFE', '#FE8FB5', '#FFBE7B']} />
          ) : null}
          <FileUploadList
            orientation="horizontal"
            className="overflow-x-auto px-0 py-1"
          >
            {files.map((file, index) => (
              <FileUploadItem
                key={index}
                value={file}
                className="max-w-52 p-1.5"
              >
                <FileUploadItemPreview className="size-8 [&>svg]:size-5">
                  <FileUploadItemProgress variant="fill" />
                </FileUploadItemPreview>
                <FileUploadItemMetadata size="sm" />
                <FileUploadItemDelete asChild>
                  <Button
                    variant="secondary"
                    size="icon"
                    className="-top-1 -right-1 absolute size-4 shrink-0 cursor-pointer rounded-full"
                  >
                    <X className="size-2.5" />
                  </Button>
                </FileUploadItemDelete>
              </FileUploadItem>
            ))}
          </FileUploadList>
          <Textarea
            value={input}
            onChange={onInputChange}
            onKeyDown={onKeyDown}
            placeholder="Ask anything NDIS related ..."
            className="w-full resize-none border-0 rounded-none bg-transparent p-0 shadow-none focus-visible:ring-0 dark:bg-transparent"
            disabled={isUploading}
          />
          <div className="absolute right-[8px] bottom-[7px] flex items-center gap-1.5">
            {
              <Button
                type="submit"
                size="icon"
                className="size-7 rounded-sm"
                disabled={!input.trim() || isUploading || isLoading}
              >
                <ArrowUp className="size-3.5" />
                <span className="sr-only">Send message</span>
              </Button>
            }
          </div>
        </form>
      </FileUpload>
      <ResultsDisplay
        isLoading={isLoading}
        endpoint={selectedApi}
        results={response}
      />
    </>
  );
}
