import { forwardRef, useImperativeHandle } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Textarea } from '@/components/ui/Textarea';
import { tr } from '@/i18n/tr';
import type { CustomContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const schema = z.object({ text: z.string().min(1, tr.cvBuilder.requiredField) });

interface CustomSectionProps {
  defaultContent: CustomContent;
}

export const CustomSection = forwardRef<SectionFormHandle<CustomContent>, CustomSectionProps>(
  ({ defaultContent }, ref) => {
    const { register, handleSubmit, formState } = useForm<CustomContent>({
      resolver: zodResolver(schema),
      defaultValues: defaultContent,
    });

    useImperativeHandle(ref, () => ({
      validate: () =>
        new Promise((resolve) => {
          handleSubmit(
            (data) => resolve(data),
            () => resolve(null),
          )();
        }),
    }));

    return (
      <Textarea
        label={tr.cvBuilder.fields.text}
        rows={5}
        error={formState.errors.text?.message}
        {...register('text')}
      />
    );
  },
);

CustomSection.displayName = 'CustomSection';
