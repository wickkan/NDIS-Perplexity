import { ENDPOINTS } from '@/lib/constants';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkLinkCitations from '@/lib/remark-link-citations';

export interface DecodeResponse {
  codes: string[];
  formatted_results: string[];
  explanation: string;
  error?: string;
}

export interface PolicyGuidanceResponse {
  guidance: string;
  citations: string[];
  related_codes: Array<{
    code: string;
    name: string;
  }>;
  error?: string;
}

export interface ServiceRecommendation {
  code: string;
  name: string;
  price: string;
  service_type: string;
}

export interface RecommendServicesResponse {
  recommendation: string;
  service_types: string[];
  recommended_codes: ServiceRecommendation[];
  error?: string;
}

export interface NDISUpdate {
  title: string;
  effective_date?: string;
  description: string;
}

export interface NDISUpdatesResponse {
  updates_summary: string;
  sources: string[];
  key_updates: NDISUpdate[];
  last_updated: string;
  error?: string;
}

export interface BudgetAllocationDetails {
  amount: number;
  percentage: number;
}

export interface BudgetAllocation {
  [category: string]: BudgetAllocationDetails;
}

export interface RecommendedBudgetCode {
  code: string;
  name: string;
  price: string;
}

export interface BudgetPlanningResponse {
  plan_amount: number;
  allocation_summary: string;
  budget_allocation: BudgetAllocation;
  recommended_codes: {
    [category: string]: RecommendedBudgetCode[];
  };
  error?: string;
}

interface ParsedNDISCode {
  code: string;
  description: string;
  prices: {
    [location: string]: string;
  };
  rules: string[];
}

const parseFormattedResult = (result: string): ParsedNDISCode => {
  const lines = result.split('\n');
  const code = lines[0].replace('Item Code: ', '');
  const description = lines[1].replace('Description: ', '');
  const pricesLine = lines[2].replace('Price Cap: ', '');
  const rulesLine = lines[3].replace('Rules: ', '');

  // Parse prices into a structured object
  const prices: { [key: string]: string } = {};
  if (pricesLine !== 'Price not specified') {
    pricesLine.split(', ').forEach((price) => {
      const [amount, location] = price.split(' for ');
      prices[location] = amount;
    });
  }

  // Parse rules into an array
  const rules = rulesLine.split(', ');

  return {
    code,
    description,
    prices,
    rules,
  };
};

const ResultsDecode = ({ results }: { results: DecodeResponse }) => {
  return (
    <>
      <div className="mb-4">
        <h3 className="font-medium text-gray-700 mb-2">NDIS Codes:</h3>
        {results?.codes && results.codes.length > 0 ? (
          <ul className="list-disc pl-5">
            {results.codes.map((code, index) => (
              <li key={index} className="text-ndis-blue font-medium">
                {code}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 italic">
            No specific NDIS codes identified
          </p>
        )}
      </div>

      {results?.formatted_results && results.formatted_results.length > 0 && (
        <div className="mb-4 space-y-4">
          <h3 className="font-medium text-gray-700 mb-2">Code Details:</h3>
          {results.formatted_results.map((result, index) => {
            const parsed = parseFormattedResult(result);
            return (
              <div
                key={index}
                className="border rounded-lg p-4 bg-white shadow-sm"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row gap-2 justify-between items-start mb-2">
                  <h4 className="text-ndis-blue font-medium">{parsed.code}</h4>
                  <div className="flex flex-wrap justify-end gap-1">
                    {parsed.rules.map((rule, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
                      >
                        {rule}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Description */}
                <p className="text-gray-700 mb-3">{parsed.description}</p>

                {/* Pricing Grid */}
                {Object.keys(parsed.prices).length > 0 ? (
                  <div className="space-y-2">
                    <h5 className="text-sm font-medium text-gray-600">
                      Price Caps:
                    </h5>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                      {Object.entries(parsed.prices).map(
                        ([location, price]) => (
                          <div
                            key={location}
                            className="flex flex-col justify-between bg-gray-50 p-2 rounded text-sm"
                          >
                            <span className="text-gray-600">{location}:</span>
                            <span className="font-medium">{price}</span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 italic">
                    Price not specified
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {results?.explanation && (
        <div>
          <h3 className="font-medium text-gray-700 mb-2">Explanation:</h3>
          <div className="bg-gray-50 p-3 rounded text-gray-700">
            <Markdown remarkPlugins={[remarkGfm]}>
              {results.explanation}
            </Markdown>
          </div>
        </div>
      )}
    </>
  );
};

const ResultsRecommend = ({
  results,
}: {
  results: RecommendServicesResponse;
}) => {
  // Group codes by service type
  const groupedCodes = results.recommended_codes.reduce((acc, code) => {
    const group = acc[code.service_type] || [];
    acc[code.service_type] = [...group, code];
    return acc;
  }, {} as Record<string, ServiceRecommendation[]>);

  return (
    <>
      {/* Service Types Section */}
      {results?.service_types && results.service_types.length > 0 && (
        <div className="mb-6">
          <h3 className="font-medium text-gray-700 mb-2">Service Types:</h3>
          <div className="flex flex-wrap gap-2">
            {results.service_types.map((type, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-ndis-blue/10 text-ndis-blue"
              >
                {type}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Main Recommendation */}
      <div className="mb-6">
        <h3 className="font-medium text-gray-700 mb-2">
          Detailed Recommendation:
        </h3>
        <div className="prose prose-gray max-w-none bg-gray-50 p-4 rounded-lg">
          <Markdown
            remarkPlugins={[remarkGfm]}
            components={{
              h2: ({ children }) => (
                <h2 className="text-lg font-semibold text-gray-800 mt-4 mb-2">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-base font-medium text-gray-700 mt-3 mb-2">
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p className="text-gray-600 mb-3 leading-relaxed">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="list-disc pl-5 space-y-1 mb-4 text-gray-600">
                  {children}
                </ul>
              ),
              li: ({ children }) => (
                <li className="leading-relaxed">{children}</li>
              ),
            }}
          >
            {results.recommendation}
          </Markdown>
        </div>
      </div>

      {/* Recommended Services Grid */}
      <div className="space-y-6">
        <h3 className="font-medium text-gray-700">Recommended Services:</h3>
        {Object.entries(groupedCodes).map(([serviceType, codes]) => (
          <div key={serviceType} className="space-y-3">
            <h4 className="text-sm font-medium text-gray-600 capitalize">
              {serviceType}:
            </h4>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {codes.map((code) => (
                <div
                  key={code.code}
                  className="border rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="space-y-1">
                      <h5 className="text-ndis-blue font-medium">
                        {code.code}
                      </h5>
                      <p className="text-gray-700">{code.name}</p>
                    </div>
                  </div>
                  {code.price !== 'Price not specified' ? (
                    <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                      <details className="group">
                        <summary className="cursor-pointer hover:text-gray-900">
                          View Price Details
                        </summary>
                        <div className="mt-2 space-y-1 pl-2">
                          {code.price.split(', ').map((priceItem, idx) => (
                            <p key={idx}>{priceItem}</p>
                          ))}
                        </div>
                      </details>
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-gray-500 italic">
                      Price not specified
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

const ResultsUpdates = ({ results }: { results: NDISUpdatesResponse }) => {
  // Function to extract reference numbers from text
  const extractReferences = (text: string) => {
    const referenceRegex = /\[(\d+)\]/g;
    const references = new Set<string>();
    let match;

    while ((match = referenceRegex.exec(text)) !== null) {
      references.add(match[1]);
    }

    return Array.from(references).sort((a, b) => parseInt(a) - parseInt(b));
  };

  // Get all references from the updates summary and descriptions
  const allReferences = new Set<string>();
  const summaryRefs = extractReferences(results.updates_summary);
  summaryRefs.forEach(ref => allReferences.add(ref));
  
  if (results?.key_updates) {
    results.key_updates.forEach(update => {
      const descriptionRefs = extractReferences(update.description);
      descriptionRefs.forEach(ref => allReferences.add(ref));
    });
  }

  const referenceArray = Array.from(allReferences).sort((a, b) => parseInt(a) - parseInt(b));

  return (
    <>
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold text-gray-800 text-lg">Latest NDIS Updates</h3>
          <span className="text-sm text-gray-500">
            Last updated: {results.last_updated}
          </span>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg shadow-sm text-gray-700">
          <div className="prose prose-gray max-w-none">
            <Markdown 
              remarkPlugins={[remarkGfm, remarkLinkCitations]}
              components={{
                h2: ({ children }) => (
                  <h2 className="text-lg font-semibold text-gray-800 mt-6 mb-3">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-base font-medium text-gray-700 mt-4 mb-2">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-gray-600 mb-3 leading-relaxed">{children}</p>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-800">
                    {children}
                  </strong>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-5 space-y-1 mb-4 text-gray-600">
                    {children}
                  </ul>
                ),
                li: ({ children }) => (
                  <li className="leading-relaxed">{children}</li>
                ),
              }}
            >
              {results.updates_summary}
            </Markdown>
          </div>
        </div>
      </div>

      {results?.key_updates && results.key_updates.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-800 text-lg mb-3">Key Policy Updates</h3>
          <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
            <div className="space-y-5">
              {results.key_updates.map((update, index) => (
                <div
                  key={update.title}
                  className="pb-5 border-b border-gray-200 last:border-0 last:pb-0"
                >
                  <h4 className="font-semibold text-ndis-blue text-base mb-2">{update.title}</h4>
                  {update.effective_date && (
                    <p className="text-sm text-gray-600 mb-3">
                      <strong>Effective from:</strong> {update.effective_date}
                    </p>
                  )}
                  <div className="prose prose-gray max-w-none text-gray-700">
                    <Markdown 
                      remarkPlugins={[remarkGfm, remarkLinkCitations]}
                      components={{
                        p: ({ children }) => (
                          <p className="text-gray-600 mb-3 leading-relaxed">{children}</p>
                        ),
                        strong: ({ children }) => (
                          <strong className="font-semibold text-gray-800">
                            {children}
                          </strong>
                        ),
                        ul: ({ children }) => (
                          <ul className="list-disc pl-5 space-y-1 mb-4 text-gray-600">
                            {children}
                          </ul>
                        ),
                        li: ({ children }) => (
                          <li className="leading-relaxed">{children}</li>
                        ),
                      }}
                    >
                      {update.description}
                    </Markdown>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {results?.sources && results.sources.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-800 text-lg mb-3">Sources</h3>
          <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
            <ul className="list-disc pl-5 text-gray-600 space-y-1">
              {results.sources.map((source, index) => (
                <li key={index} className="text-sm">{source}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Hidden anchor points for citation links */}
      <div className="hidden">
        {referenceArray.map((refNumber) => (
          <span key={refNumber} id={`ref-${refNumber}`}></span>
        ))}
      </div>
    </>
  );
};

const ResultsPolicy = ({ results }: { results: PolicyGuidanceResponse }) => {
  // Function to extract reference numbers from text
  const extractReferences = (text: string) => {
    const referenceRegex = /\[(\d+)\]/g;
    const references = new Set<string>();
    let match;

    while ((match = referenceRegex.exec(text)) !== null) {
      references.add(match[1]);
    }

    return Array.from(references).sort((a, b) => parseInt(a) - parseInt(b));
  };

  // Get all references from the guidance text
  const guidanceRefs = extractReferences(results?.guidance || '');
  
  return (
    <>
      {/* Main guidance content */}
      <div className="mb-6">
        <div className="prose prose-gray max-w-none">
          <Markdown
            remarkPlugins={[remarkGfm, remarkLinkCitations]}
            components={{
              h2: ({ children }) => (
                <h2 className="text-lg font-semibold text-gray-800 mt-6 mb-3">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-base font-medium text-gray-700 mt-4 mb-2">
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p className="text-gray-600 mb-3 leading-relaxed">{children}</p>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-gray-800">
                  {children}
                </strong>
              ),
              ul: ({ children }) => (
                <ul className="list-disc pl-5 space-y-1 mb-4 text-gray-600">
                  {children}
                </ul>
              ),
              li: ({ children }) => (
                <li className="leading-relaxed">{children}</li>
              ),
            }}
          >
            {results?.guidance}
          </Markdown>
        </div>
      </div>

      {/* Related codes section */}
      {results?.related_codes && results.related_codes.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            Related NDIS Codes
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {results.related_codes.map((code) => (
              <div
                key={code.code}
                className="border rounded-lg p-3 bg-white shadow-sm"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium text-ndis-blue">
                    {code.code}
                  </span>
                  <span className="text-gray-600">-</span>
                  <span className="text-gray-700">{code.name}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citations section - renamed to Sources for consistency */}
      {results?.citations && results.citations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            Sources
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
            <ul className="list-disc space-y-2 pl-5">
              {results.citations.map((citation, index) => (
                <li key={index} className="text-sm text-gray-600">
                  <Markdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({ children }) => <span>{children}</span>,
                      a: ({ children, href }) => (
                        <a
                          href={href}
                          className="text-ndis-blue hover:underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {children}
                        </a>
                      ),
                    }}
                  >
                    {citation}
                  </Markdown>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Hidden anchor points for citation links */}
      <div className="hidden">
        {guidanceRefs.map((refNumber) => (
          <span key={refNumber} id={`ref-${refNumber}`}></span>
        ))}
      </div>
    </>
  );
};

const ResultsBudget = ({ results }: { results: BudgetPlanningResponse }) => {
  // Function to extract reference numbers from text
  const extractReferences = (text: string) => {
    const referenceRegex = /\[(\d+)\]/g;
    const references = new Set<string>();
    let match;

    while ((match = referenceRegex.exec(text)) !== null) {
      references.add(match[1]);
    }

    return Array.from(references).sort((a, b) => parseInt(a) - parseInt(b));
  };

  // Get all references from the allocation summary
  const summaryRefs = extractReferences(results.allocation_summary || '');
  
  return (
    <>
      {/* Main budget summary content */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-800 text-lg mb-3">Budget Allocation Plan</h3>
        <div className="bg-gray-50 p-4 rounded-lg shadow-sm text-gray-700">
          <div className="prose prose-gray max-w-none">
            <div className="flex justify-between items-center mb-4">
              <span className="font-medium text-gray-700">Total NDIS Plan Amount:</span>
              <span className="text-lg font-semibold text-ndis-blue">
                ${results.plan_amount?.toLocaleString()}
              </span>
            </div>
            <Markdown 
              remarkPlugins={[remarkGfm, remarkLinkCitations]}
              components={{
                h2: ({ children }) => (
                  <h2 className="text-lg font-semibold text-gray-800 mt-6 mb-3">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-base font-medium text-gray-700 mt-4 mb-2">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-gray-600 mb-3 leading-relaxed">{children}</p>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-800">
                    {children}
                  </strong>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-5 space-y-1 mb-4 text-gray-600">
                    {children}
                  </ul>
                ),
                li: ({ children }) => (
                  <li className="leading-relaxed">{children}</li>
                ),
              }}
            >
              {results.allocation_summary}
            </Markdown>
          </div>
        </div>
      </div>

      {/* Only show recommended services if available */}
      {Object.keys(results.recommended_codes || {}).length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-800 text-lg mb-3">Recommended NDIS Services</h3>
          <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
            <div className="space-y-5">
              {Object.entries(results.recommended_codes || {}).map(
                ([category, codes]) => (
                  <div key={category} className="space-y-3 pb-4 border-b border-gray-200 last:border-0">
                    <h4 className="font-medium text-ndis-blue">
                      {category}
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {codes.map((code) => (
                        <div
                          key={code.code}
                          className="flex flex-col border rounded-lg p-3 bg-white shadow-sm"
                        >
                          <div className="flex justify-between">
                            <span className="font-medium text-gray-800">{code.code}</span>
                            <span className="text-sm font-medium text-gray-600">{code.price}</span>
                          </div>
                          <span className="text-sm text-gray-700 mt-1">{code.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      )}

      {/* Hidden anchor points for citation links */}
      <div className="hidden">
        {summaryRefs.map((ref) => (
          <span key={ref} id={`ref-${ref}`}></span>
        ))}
      </div>
    </>
  );
};

const ResultsLoading = () => {
  return (
    <div className="border shadow-md rounded-lg p-6">
      <div className="h-7 w-48 bg-gray-200 rounded-md mb-6 animate-pulse" />

      {/* Primary Content Section */}
      <div className="mb-4">
        <div className="h-5 w-32 bg-gray-200 rounded-md mb-3 animate-pulse" />
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center space-x-2">
              <div className="h-4 w-24 bg-gray-100 rounded animate-pulse" />
              <div className="h-4 w-48 bg-gray-100 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>

      {/* Secondary Content Section */}
      <div className="mb-4">
        <div className="h-5 w-40 bg-gray-200 rounded-md mb-3 animate-pulse" />
        <div className="h-24 bg-gray-100 rounded-md animate-pulse" />
      </div>

      {/* Related Items Grid */}
      <div className="mb-4">
        <div className="h-5 w-36 bg-gray-200 rounded-md mb-3 animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-12 border rounded-md bg-gray-50 animate-pulse"
            />
          ))}
        </div>
      </div>

      {/* Citations/Sources Section */}
      <div>
        <div className="h-5 w-28 bg-gray-200 rounded-md mb-3 animate-pulse" />
        <div className="space-y-1">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="h-4 w-full bg-gray-100 rounded animate-pulse"
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const ResultsError = ({ error }: { error: string }) => {
  return (
    <div className="border border-red-200 shadow-sm rounded-lg p-6">
      <div className="flex items-start space-x-3">
        <div className="min-w-fit p-2 bg-red-100 rounded-full">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            className="w-5 h-5 text-red-600"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <div className="space-y-1">
          <h3 className="font-medium text-red-900">Error Processing Request</h3>
          <p className="text-sm text-red-600">{error}</p>
          <p className="text-xs text-red-500">
            Please try again or contact support if the issue persists.
          </p>
        </div>
      </div>
    </div>
  );
};

/**
 * Component to display NDIS decoding results
 */
const ResultsDisplay = ({
  endpoint,
  results,
  isLoading,
}: {
  endpoint: string;
  results: any;
  isLoading?: boolean;
}) => {
  if (isLoading) return <ResultsLoading />;
  if (!results) return null;
  if (results.error) return <ResultsError error={results.error} />;

  const title =
    endpoint === ENDPOINTS.NDIS_UPDATES.url
      ? ENDPOINTS.NDIS_UPDATES.name
      : endpoint === ENDPOINTS.POLICY_SERVICES.url
      ? ENDPOINTS.POLICY_SERVICES.name
      : endpoint === ENDPOINTS.DECODE.url
      ? ENDPOINTS.DECODE.name
      : endpoint === ENDPOINTS.PLAN_BUDGET.url
      ? ENDPOINTS.PLAN_BUDGET.name
      : 'NDIS';

  return (
    <div className="border shadow-md rounded-lg p-6">
      <h2 className="text-xl font-semibold text-ndis-dark mb-4">{title}</h2>

      {endpoint === ENDPOINTS.DECODE.url ? (
        <ResultsDecode results={results} />
      ) : endpoint === ENDPOINTS.POLICY_SERVICES.url ? (
        <ResultsPolicy results={results} />
      ) : endpoint === ENDPOINTS.NDIS_UPDATES.url ? (
        <ResultsUpdates results={results} />
      ) : endpoint === ENDPOINTS.PLAN_BUDGET.url ? (
        <ResultsBudget results={results} />
      ) : null}
    </div>
  );
};

export default ResultsDisplay;
