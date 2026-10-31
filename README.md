# Automation Foundry AI (AFAI)

**Physical AI Engineering Copilot**  
*Turn engineering experience into deployable robotic intelligence.*

Automation Foundry AI is an emerging AI-powered engineering knowledge and integration platform for industrial robotics. The initial focus is helping robotics integrators and engineering teams reuse lessons from technical videos, project reports, vendor documentation, and previous automation projects.

> **Project status:** Early-stage product. The applications linked below are existing IdeaFactory tools and technical foundations; they are **not** evidence that the integrated AFAI platform is commercially validated.

## Quick links

| Resource | Link |
| --- | --- |
| **AFAI landing page** | [Open website](https://luisalbertomunozubando.github.io/AFAI/) |
| **Free community signup (activation pending)** | [Join the community](https://luisalbertomunozubando.github.io/AFAI/community.html) |
| **Business Model Canvas & Customer Value** | [View business model](https://luisalbertomunozubando.github.io/AFAI/business-model.html) |
| **AFAI source repository** | [GitHub repository](https://github.com/LuisAlbertoMunozUbando/AFAI) |
| **IdeaFactory application portfolio** | [Explore IdeaFactory](https://luisalbertomunozubando.github.io/IdeaFactory/) |
| **Founder profile and CV** | [Prof. Alberto Muñoz](https://cv.albertomunoz.ai) |
| **Industrial pilot enquiries** | [Contact by email](mailto:contact@albertomunoz.ai?subject=Automation%20Foundry%20AI%20Pilot%20Enquiry) |

## Community newsletter signup — Google Sheets integration

The [community signup page](https://luisalbertomunozubando.github.io/AFAI/community.html) is published, but **submissions are intentionally disabled until the secure receiving endpoint and privacy arrangements are activated**. Do not describe it as collecting subscriptions yet.

Subscriber data will be stored in a private native Google Sheet named **AFAI - Community Newsletter and Industrial Challenges**, tab **Subscribers**. It includes contact information, company, AI/robotics roles, challenges, topic preferences, and explicit consent flags.

**Activation steps for the repository owner:**

1. Open the [private subscriber spreadsheet](https://docs.google.com/spreadsheets/d/1LOPjtL2iS4WYe3pL1RqobwnNQW3Rb1busFATAMpXGvc/edit).
2. Choose **Extensions → Apps Script** and paste [google-apps-script/Code.gs](./google-apps-script/Code.gs).
3. Review the script, security, consent, unsubscribe procedure, data retention, and privacy policy. Deploy as a Web App running **as the owner**, accessible to **Anyone**. **Never share the private spreadsheet publicly.**
4. Copy the deployment's `https://script.google.com/macros/s/.../exec` URL into `ENDPOINT` near the bottom of [community.html](./community.html), replacing the empty string. Commit the change.
5. Test with a non-sensitive test record, verify a row appears in the **Subscribers** tab, test failure cases and duplicates, and then announce that registration is live.
6. Maintain an opt-out process before sending newsletters; the form does not automatically send emails.

**Security note:** Public Apps Script endpoints may be abused by bots. Consider CAPTCHA, rate limiting, a managed form provider, and a fuller privacy notice before production launch. This is a starter integration, not a production-grade CRM.

## Existing AI applications

These are the **five applications directly linked from the current landing page**. Their activity indicators describe different measurements and should not be combined into a count of unique active users or paying customers.

| Application | Open application | Purpose | Reported activity |
| --- | --- | --- | --- |
| **YouTube2Knowledge** | [youtube2knowledge.albertomunoz.ai](https://youtube2knowledge.albertomunoz.ai) | Video transcription and structured knowledge extraction | 329 recorded uses; 104 jobs in the latest monitoring period |
| **VisionFromYouTube** | [visionfromyoutube.albertomunoz.ai](https://visionfromyoutube.albertomunoz.ai) | Visual information extraction and analysis from video | 21,234 historical documents processed; 174 additional processing activities |
| **Knowledge** | [knowledge.albertomunoz.ai](https://knowledge.albertomunoz.ai) | AI-powered knowledge retrieval and document analysis | 69 usage reports; 221 recent actions (46 questions, 127 searches, 48 uploads) |
| **Science–Technology Landscape (STL)** | [stl.albertomunoz.ai](https://stl.albertomunoz.ai) | Scientific and technology landscape analysis | 15 reported users; 18 analyses |
| **Innovaction** | [innovaction.albertomunoz.ai](https://innovaction.albertomunoz.ai) | AI-assisted innovation and idea-development workflows | 93 reported users; 14 generations |

**Additional IdeaFactory applications:** The wider portfolio includes eight working applications. See the [IdeaFactory portfolio](https://luisalbertomunozubando.github.io/IdeaFactory/) for the complete catalogue; this README lists only the five individual application URLs currently published on the AFAI landing page.

## Explore the landing page

- [Overview — Physical AI Engineering Copilot](https://luisalbertomunozubando.github.io/AFAI/#top)
- [Business Model Canvas — customers, value, pricing and ROI](https://luisalbertomunozubando.github.io/AFAI/business-model.html)
- [The engineering knowledge problem](https://luisalbertomunozubando.github.io/AFAI/#problem)
- [How Automation Foundry works](https://luisalbertomunozubando.github.io/AFAI/#how)
- [Technology and integration vision](https://luisalbertomunozubando.github.io/AFAI/#technology)
- [Existing AI applications](https://luisalbertomunozubando.github.io/AFAI/#applications)
- [Enquire about an industrial pilot](mailto:contact@albertomunoz.ai?subject=Automation%20Foundry%20AI%20Pilot%20Enquiry)

## What we are building

1. **Capture engineering experience:** Extract structured knowledge from demonstrations, documentation, reports, and project histories.
2. **Find relevant precedents:** Search for comparable automation challenges, equipment, approaches, failures, and outcomes.
3. **Support engineering decisions:** Provide evidence-backed suggestions that engineers can evaluate and validate.
4. **Enable reusable integration:** Progressively connect engineering knowledge with Physical AI, perception, planning, simulation, and robotics tools.
5. **Keep humans in control:** Explore interactive supervision and agents that can ask engineers for guidance when uncertain.

The longer-term vision is a reusable engineering integration layer for Physical AI. This is a product direction, **not a claim that all these capabilities are currently deployed**.

## Project and technical notes

- **Website source:** [index.html](./index.html)
- **Deployment:** GitHub Pages from the `main` branch.
- **Existing AI foundation:** Python, PyTorch, CUDA, NVIDIA DGX Spark, multimodal processing, retrieval-augmented generation, and API-based services.
- **Planned AFAI integration:** Structured engineering cases, semantic search, private knowledge bases, evidence-backed recommendations, and potential integration with ROS 2 and simulation ecosystems.
- **Privacy:** Do not submit confidential industrial documents or proprietary IP to a public demo without appropriate agreements and safeguards.
- **Engineering safety:** AI-generated suggestions require qualified human verification before use on physical equipment.

## Contact

**Industrial pilots, robotics integration partnerships, and feedback:**  
[contact@albertomunoz.ai](mailto:contact@albertomunoz.ai)

*Note: The email address above is the contact address currently shown on the landing page and should be confirmed before external outreach.*

---

**Not just faster robots. Faster engineering. Faster integration. Faster value creation.**
