from fuzzywuzzy import fuzz

api_answers = [
    "The policy does not specify a grace period.",
    "Covered after 36 months of continuous coverage",
    "Yes, this policy covers maternity expenses under Section 3.1.14, defined as medical treatment expenses traceable to childbirth (including complicated deliveries and caesarean sections incurred during Hospitalization) and expenses towards lawful medical termination of pregnancy during the Policy Period.\n\nConditions:\n*   The female Insured Person should have been continuously covered for at least 24 months before availing this benefit, unless waived in case of delivery, miscarriage or abortion induced by accident.\n*   The Covered female Insured Person must be between eighteen (18) years and forty-five (45) years of age.\n*   Coverage is limited to two deliveries or terminations or either has been paid under the Policy and its Renewals.\n*   Only one delivery or lawful medical termination of pregnancy is covered during a single Policy Period.\n*   The policy excludes maternity expenses of Surrogate Mother, unless claim is admitted under Section 3.1.15 (Infertility).\n*   Ectopic pregnancy is excluded under Maternity Expenses but covered under ‘In-patient treatment’, provided such pregnancy is established by medical reports.\n*   Pre and post hospitalisation expenses, other than pre and post natal treatment are not covered.\n*   New Born Baby shall be automatically covered from birth under the Sum Insured available to the mother during the corresponding Policy Period, for up to 3 months of age. On attaining 3 months of age, the New Born Baby shall be covered only if specifically included in the Policy mid-term and requisite premium paid.",
    "Two years",
    "Yes, the Company shall indemnify the Medical Expenses incurred in respect of an organ donor’s Hospitalisation during the Policy Period for harvesting of the organ donated to an Insured Person, provided that:\ni. The organ donation confirms to the Transplantation of Human Organs Act 1994 (and its amendments from time to time)\nii. The organ is used for an Insured Person and the Insured Person has been medically advised to undergo an organ transplant\niii. The Medical Expenses shall be incurred in respect of the organ donor as an in-patient in a Hospital.\niv. Claim has been admitted under In-patient Treatment Section in respect of the Insured Person undergoing the organ transplant.\nExclusions:\ni. Pre-hospitalization Medical Expenses or Post- Hospitalization Medical Expenses of the organ donor.\nii. Costs directly or indirectly associated with the acquisition of the donor’s organ.\niii. Medical Expenses where the organ transplant is experimental or investigational.\niv. Any medical treatment or complication in respect of the donor, consequent to harvesting.\nv. Any expenses related to organ transportation or preservation.",
    "The provided policy excerpts do not contain information about the No Claim Discount (NCD).",
    "The provided policy excerpts do not mention any benefit for preventive health check-ups.",
    "The policy excerpts provided do not contain a specific definition of the term \"Hospital.\"",
    "The Company shall indemnify Medical Expenses incurred for Inpatient Care treatment under Ayurveda, Yoga and Naturopathy, Unani, Siddha and Homeopathy systems of medicines during each Policy Period up to the limit of Sum Insured as specified in the Policy Schedule in any AYUSH Hospital.",
    "Yes, for Plan A, room charges are limited to up to 1% of the Sum Insured or actual charges, whichever is lower, and ICU charges are limited to up to 2% of the Sum Insured or actual charges, whichever is lower. However, the limit shall not apply if the treatment is undergone for a listed procedure in a Preferred Provider Network (PPN) as a package."
]

desired_answers = [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
    "The policy has a specific waiting period of two (2) years for cataract surgery.",
    "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
    "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
    "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
    "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
    "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
    "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
]

scores = []
for api, desired in zip(api_answers, desired_answers):
    score = fuzz.token_sort_ratio(api, desired)
    scores.append(score)
    print(f"Score: {score}%\nAPI: {api}\nDESIRED: {desired}\n{'-'*60}")

print(f"Average match: {sum(scores)/len(scores):.2f}%")