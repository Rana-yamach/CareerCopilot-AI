import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { ExperienceContent, ExperienceItem } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  title: z.string().min(1, tr.cvBuilder.requiredField),
  company: z.string().min(1, tr.cvBuilder.requiredField),
  start_date: z.string().min(1, tr.cvBuilder.requiredField),
  end_date: z.string().min(1, tr.cvBuilder.requiredField),
  description: z.string().min(1, tr.cvBuilder.requiredField),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: ExperienceItem = {
  title: '',
  company: '',
  start_date: '',
  end_date: '',
  description: '',
};

interface ExperienceSectionProps {
  defaultContent: ExperienceContent;
}

export const ExperienceSection = forwardRef<
  SectionFormHandle<ExperienceContent>,
  ExperienceSectionProps
>(({ defaultContent }, ref) => {
  const { form, fieldArray } = useSectionItemsForm<ExperienceItem>(ref, {
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
            label={tr.cvBuilder.fields.jobTitle}
            error={errors?.[index]?.title?.message}
            {...register(`items.${index}.title`)}
          />
          <Input
            label={tr.cvBuilder.fields.company}
            error={errors?.[index]?.company?.message}
            {...register(`items.${index}.company`)}
          />
          <Input
            label={tr.cvBuilder.fields.startDate}
            type="month"
            error={errors?.[index]?.start_date?.message}
            {...register(`items.${index}.start_date`)}
          />
          <Input
            label={tr.cvBuilder.fields.endDate}
            type="month"
            error={errors?.[index]?.end_date?.message}
            {...register(`items.${index}.end_date`)}
          />
          <div className="sm:col-span-2">
            <Textarea
              label={tr.cvBuilder.fields.description}
              error={errors?.[index]?.description?.message}
              {...register(`items.${index}.description`)}
            />
          </div>
        </ItemCard>
      ))}
      <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
        + {tr.cvBuilder.addItem}
      </Button>
    </div>
  );
});

ExperienceSection.displayName = 'ExperienceSection';
