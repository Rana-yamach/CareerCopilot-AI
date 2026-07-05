import { forwardRef, useImperativeHandle } from 'react';
import { useForm } from 'react-hook-form';
import { Input } from '@/components/ui/Input';
import { tr } from '@/i18n/tr';
import type { InterestsContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

interface InterestsFormValues {
  interestsText: string;
}

interface InterestsSectionProps {
  defaultContent: InterestsContent;
}

export const InterestsSection = forwardRef<
  SectionFormHandle<InterestsContent>,
  InterestsSectionProps
>(({ defaultContent }, ref) => {
  const { register, getValues } = useForm<InterestsFormValues>({
    defaultValues: { interestsText: defaultContent.items.join(', ') },
  });

  useImperativeHandle(ref, () => ({
    validate: async () => {
      const { interestsText } = getValues();
      return {
        items: interestsText
          .split(',')
          .map((v) => v.trim())
          .filter(Boolean),
      };
    },
  }));

  return (
    <Input
      label={tr.cvBuilder.interestsLabel}
      hint={tr.cvBuilder.interestsHint}
      {...register('interestsText')}
    />
  );
});

InterestsSection.displayName = 'InterestsSection';
