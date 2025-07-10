import Chat from '@/components/invoice-chat';
import { AuroraText } from '@/components/magicui/aurora-text';

const Homepage = () => {
  return (
    <div className="flex flex-col gap-6 items-stretch justify-center m-auto px-4 mt-56 sm:mt-72 max-w-lg sm:max-w-screen-lg">
      <span className="text-xl tracking-tight md:text-2xl lg:text-3xl">
        👋 Hi there, Welcome to Decode{' '}
        <AuroraText>
          <strong>NDIS</strong>
        </AuroraText>
        , how can I help you today?
      </span>
      <div className="flex flex-col gap-4">
        <Chat />
      </div>
    </div>
  );
};

export default Homepage;
