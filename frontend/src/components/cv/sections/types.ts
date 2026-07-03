/**
 * CV Builder bölüm formlarının ortak arayüzü. Her bölüm component'i bu
 * handle'ı `forwardRef` ile dışa açar; `CVBuilderFormPage` submit sırasında
 * tüm bölümleri sırayla doğrular (bkz. TASK-127).
 */
export interface SectionFormHandle<TContent> {
  validate: () => Promise<TContent | null>;
}
