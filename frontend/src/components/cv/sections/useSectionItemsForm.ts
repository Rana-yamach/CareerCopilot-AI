import { useImperativeHandle } from 'react';
import type { Ref } from 'react';
import { useFieldArray, useForm } from 'react-hook-form';
import type { UseFormReturn } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import type { ZodType } from 'zod';
import type { SectionFormHandle } from './types';

interface UseSectionItemsFormOptions<TItem extends object> {
  schema: ZodType<{ items: TItem[] }>;
  defaultItems: TItem[];
}

/** `useFieldArray`'in minimal, bölüm component'lerinin ihtiyaç duyduğu kısmı. */
export interface ItemsFieldArray<TItem> {
  fields: (TItem & { id: string })[];
  append: (item: TItem) => void;
  remove: (index: number) => void;
}

/**
 * "items" dizisi barındıran bölüm formları (Eğitim, Deneyim, Diller vb.)
 * için ortak React Hook Form + useFieldArray kurulumu.
 *
 * Not: `TItem` çağıran component'e göre değiştiği için react-hook-form'un
 * `ArrayPath<T>` tip çıkarımı generic sınırda çözülemiyor (bilinen bir
 * react-hook-form + generic wrapper kısıtı). Bu nedenle dahili `useForm` /
 * `useFieldArray` çağrıları `any` ile gevşetilip, dışa yalnızca ihtiyaç
 * duyulan minimal ve tip güvenli `ItemsFieldArray<TItem>` arayüzü sunulur.
 */
export function useSectionItemsForm<TItem extends object>(
  ref: Ref<SectionFormHandle<{ items: TItem[] }>>,
  { schema, defaultItems }: UseSectionItemsFormOptions<TItem>,
) {
  type FormValues = { items: TItem[] };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const form = useForm<any>({
    resolver: zodResolver(schema),
    defaultValues: { items: defaultItems },
  }) as UseFormReturn<FormValues>;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fieldArray = useFieldArray({
    control: form.control as never,
    name: 'items' as never,
  }) as unknown as ItemsFieldArray<TItem>;

  useImperativeHandle(ref, () => ({
    // `handleSubmit` kullanılır; böylece zod resolver'ın coerce ettiği
    // (örn. `z.coerce.number()`) değerler `getValues()`'un aksine doğru
    // tipte döner.
    validate: () =>
      new Promise((resolve) => {
        form.handleSubmit(
          (data) => resolve(data as FormValues),
          () => resolve(null),
        )();
      }),
  }));

  return { form, fieldArray };
}
