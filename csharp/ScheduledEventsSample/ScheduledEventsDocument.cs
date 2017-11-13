/* Copyright 2014 Microsoft Corporation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
*/

namespace ScheduledEventsSample
{
    using System;
    using System.Collections.Generic;
    using System.Runtime.Serialization;

    /// <summary>
    /// Represents the entire Scheduled Events document
    /// </summary>
    [DataContract]
    public class ScheduledEventsDocument
    {
        [DataMember]
        public string DocumentIncarnation;

        [DataMember]
        public List<ScheduledEvent> Events { get; set; }
    }

    /// <summary>
    /// Represents an individual scheduled event
    /// </summary>
    [DataContract]
    public class ScheduledEvent
    {
        [DataMember]
        public string EventId { get; set; }

        [DataMember]
        public string EventStatus { get; set; }

        [DataMember]
        public string EventType { get; set; }

        [DataMember]
        public string ResourceType { get; set; }

        [DataMember]
        public List<string> Resources { get; set; }

        [DataMember]
        public DateTime? NotBefore { get; set; }
    }
}
