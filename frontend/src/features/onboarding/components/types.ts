export interface OnboardingFormValues {
  name: string;
  email: string;
  password: string;
  title: string;
  background: string;
  expertise: string;
  interests: { value: string }[];
  youtubeChannels: { value: string; id?: string; name?: string; handle?: string }[];
  preferences: {
    digestFrequency: string;
    format: string;
  };
}
