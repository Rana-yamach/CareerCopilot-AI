import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useCVBuilderStore } from '@/store/cvBuilderStore';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { tr } from '@/i18n/tr';
import type { SectionType } from '@/types/cv';

const sectionOrder: SectionType[] = [
  'education',
  'experience',
  'skills',
  'languages',
  'certificates',
  'interests',
  'projects',
  'courses',
  'awards',
  'organisations',
  'publications',
  'references',
  'declaration',
  'custom',
];

const personalSchema = z.object({
  name: z.string().min(1, tr.cvBuilder.fullNameRequired),
  email: z
    .string()
    .min(1, tr.cvBuilder.emailRequired)
    .email(tr.cvBuilder.emailInvalid),
  phone: z.string().optional(),
  location: z.string().optional(),
  linkedin_url: z.string().optional(),
  github_url: z.string().optional(),
});

type PersonalFormValues = z.infer<typeof personalSchema>;

export function SectionSelectPage() {
  const navigate = useNavigate();
  const personal = useCVBuilderStore((state) => state.personal);
  const selectedSections = useCVBuilderStore((state) => state.selectedSections);
  const toggleSection = useCVBuilderStore((state) => state.toggleSection);
  const setPersonal = useCVBuilderStore((state) => state.setPersonal);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PersonalFormValues>({
    resolver: zodResolver(personalSchema),
    defaultValues: {
      name: personal.name,
      email: personal.email,
      phone: personal.phone ?? '',
      location: personal.location ?? '',
      linkedin_url: personal.linkedin_url ?? '',
      github_url: personal.github_url ?? '',
    },
  });

  function onSubmit(values: PersonalFormValues) {
    if (selectedSections.length === 0) {
      toast.error(tr.cvBuilder.noSectionSelected);
      return;
    }
    setPersonal(values);
    navigate('/cv/builder/form');
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{tr.cvBuilder.sectionSelectTitle}</h1>
        <p className="mt-1 text-sm text-gray-500">{tr.cvBuilder.sectionSelectSubtitle}</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
        <div className="card space-y-4">
          <h2 className="text-base font-semibold text-gray-900">{tr.cvBuilder.personalInfo}</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input
              label={tr.cvBuilder.fullName}
              error={errors.name?.message}
              {...register('name')}
            />
            <Input
              label={tr.cvBuilder.email}
              type="email"
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              label={`${tr.cvBuilder.phone} ${tr.common.optional}`}
              error={errors.phone?.message}
              {...register('phone')}
            />
            <Input
              label={`${tr.cvBuilder.location} ${tr.common.optional}`}
              error={errors.location?.message}
              {...register('location')}
            />
            <Input
              label={`${tr.cvBuilder.linkedinUrl} ${tr.common.optional}`}
              error={errors.linkedin_url?.message}
              {...register('linkedin_url')}
            />
            <Input
              label={`${tr.cvBuilder.githubUrl} ${tr.common.optional}`}
              error={errors.github_url?.message}
              {...register('github_url')}
            />
          </div>
        </div>

        <div className="card">
          <h2 className="text-base font-semibold text-gray-900">{tr.cvBuilder.sectionsHeading}</h2>
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {sectionOrder.map((type) => (
              <label
                key={type}
                className="flex cursor-pointer items-center gap-3 rounded-lg border border-gray-200 px-4 py-3 text-sm font-medium text-gray-700 hover:border-primary-300 hover:bg-primary-50/40"
              >
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  checked={selectedSections.includes(type)}
                  onChange={() => toggleSection(type)}
                />
                {tr.cvBuilder.sections[type]}
              </label>
            ))}
          </div>
        </div>

        <div className="flex justify-end">
          <Button type="submit">{tr.cvBuilder.continueToForm}</Button>
        </div>
      </form>
    </div>
  );
}
