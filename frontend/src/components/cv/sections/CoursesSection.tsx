import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { CourseItem, CoursesContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  name: z.string().min(1, tr.cvBuilder.requiredField),
  platform: z.string().min(1, tr.cvBuilder.requiredField),
  completion_date: z.string().min(1, tr.cvBuilder.requiredField),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: CourseItem = { name: '', platform: '', completion_date: '' };

interface CoursesSectionProps {
  defaultContent: CoursesContent;
}

export const CoursesSection = forwardRef<SectionFormHandle<CoursesContent>, CoursesSectionProps>(
  ({ defaultContent }, ref) => {
    const { form, fieldArray } = useSectionItemsForm<CourseItem>(ref, {
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
              label={tr.cvBuilder.fields.name}
              error={errors?.[index]?.name?.message}
              {...register(`items.${index}.name`)}
            />
            <Input
              label={tr.cvBuilder.fields.platform}
              error={errors?.[index]?.platform?.message}
              {...register(`items.${index}.platform`)}
            />
            <Input
              label={tr.cvBuilder.fields.completionDate}
              type="month"
              error={errors?.[index]?.completion_date?.message}
              {...register(`items.${index}.completion_date`)}
            />
          </ItemCard>
        ))}
        <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
          + {tr.cvBuilder.addItem}
        </Button>
      </div>
    );
  },
);

CoursesSection.displayName = 'CoursesSection';
