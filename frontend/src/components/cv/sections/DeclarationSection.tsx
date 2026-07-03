import { forwardRef, useImperativeHandle } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Textarea } from '@/components/ui/Textarea';
import { tr } from '@/i18n/tr';
import type { DeclarationContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const schema = z.object({ text: z.string().min(1, tr.cvBuilder.requiredField) });

interface DeclarationSectionProps {
  defaultContent: DeclarationContent;
}

export const DeclarationSection = forwardRef<
  SectionFormHandle<DeclarationContent>,
  DeclarationSectionProps
>(({ defaultContent }, ref) => {
  const { register, handleSubmit, formState } = useForm<DeclarationContent>({
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
});

DeclarationSection.displayName = 'DeclarationSection';
