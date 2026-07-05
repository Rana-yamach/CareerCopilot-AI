import { forwardRef } from 'react';
import { z } from 'zod';
import { useSectionItemsForm } from './useSectionItemsForm';
import { ItemCard } from './ItemCard';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { LanguageItem, LanguagesContent } from '@/types/cv';
import type { SectionFormHandle } from './types';

const itemSchema = z.object({
  language: z.string().min(1, tr.cvBuilder.requiredField),
  level: z.string().min(1, tr.cvBuilder.requiredField),
});

const schema = z.object({ items: z.array(itemSchema) });

const defaultItem: LanguageItem = { language: '', level: '' };

interface LanguagesSectionProps {
  defaultContent: LanguagesContent;
}

export const LanguagesSection = forwardRef<
  SectionFormHandle<LanguagesContent>,
  LanguagesSectionProps
>(({ defaultContent }, ref) => {
  const { form, fieldArray } = useSectionItemsForm<LanguageItem>(ref, {
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
            label={tr.cvBuilder.fields.language}
            error={errors?.[index]?.language?.message}
            {...register(`items.${index}.language`)}
          />
          <Input
            label={tr.cvBuilder.fields.level}
            placeholder="Örn: B2, Anadil, İleri"
            error={errors?.[index]?.level?.message}
            {...register(`items.${index}.level`)}
          />
        </ItemCard>
      ))}
      <Button type="button" variant="secondary" onClick={() => fieldArray.append(defaultItem)}>
        + {tr.cvBuilder.addItem}
      </Button>
    </div>
  );
});

LanguagesSection.displayName = 'LanguagesSection';
