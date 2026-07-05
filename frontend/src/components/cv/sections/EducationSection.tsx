import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { EducationContent, EducationItem } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  degree: z.string().min(1, tr.cvBuilder.requiredField),
  institution: z.string().min(1, tr.cvBuilder.requiredField),
  year: z.coerce.number().min(1950, tr.cvBuilder.requiredField).max(2100),
  gpa: z.string().optional(),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: EducationItem = {
  degree: '',
  institution: '',
  year: new Date().getFullYear(),
  gpa: '',
};

interface EducationSectionProps {
  defaultContent: EducationContent;
}

export const EducationSection = forwardRef<
  SectionFormHandle<EducationContent>,
  EducationSectionProps
>(({ defaultContent }, ref) => {
  const { form, fieldArray } = useSectionItemsForm<EducationItem>(ref, {
    schema,
    defaultItems: defaultContent.items,
  });
  const { register, formState } = form;
  const errors = formState.errors.items;

  return (
    <div className="space-y-4">
      {fieldArray.fields.length === 0 && <EmptyState title={tr.cvBuilder.noItemsYet} />}
      {fieldArray.fields.map((field, index) => (
        <ItemCard key={field.id} index={index} onRemove={() => fieldArray.remove(index)}>
          <Input
            label={tr.cvBuilder.fields.degree}
            error={errors?.[index]?.degree?.message}
            {...register(`items.${index}.degree`)}
          />
          <Input
            label={tr.cvBuilder.fields.institution}
            error={errors?.[index]?.institution?.message}
            {...register(`items.${index}.institution`)}
          />
          <Input
            label={tr.cvBuilder.fields.year}
            type="number"
            error={errors?.[index]?.year?.message}
            {...register(`items.${index}.year`)}
          />
          <Input
            label={`${tr.cvBuilder.fields.gpa} ${tr.common.optional}`}
            {...register(`items.${index}.gpa`)}
          />
        </ItemCard>
      ))}
      <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
        + {tr.cvBuilder.addItem}
      </Button>
    </div>
  );
});

EducationSection.displayName = 'EducationSection';
